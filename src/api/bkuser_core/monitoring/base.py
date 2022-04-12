# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Type

# Apply pymysql patch
import pymysql
import redis
import requests

from .exceptions import NoDeadlyIssueError, StatusMissError, SystemNotHealthyError

logger = logging.getLogger(__name__)


@dataclass
class Issue:
    # if a issue is deadly means the main function of system is not working
    deadly: bool
    description: str

    def __str__(self):
        return f"deadly<{self.deadly}>-{self.description}"


@dataclass
class Diagnosis:
    system_name: str
    # when a system is healthy means all the function of it could work
    # well as expected and without any issue.
    healthy: bool = True
    # alive is a key field for indicating system health
    alive: bool = True
    is_core: bool = True
    issues: List[Issue] = field(default_factory=lambda: [])

    def __str__(self):
        return f"{self.system_name}-healthy<{self.healthy}>-alive{self.alive}"

    def set_dead(self, issues: List[Issue]):
        self.healthy = False
        self.alive = False
        self.issues = issues

    def get_deadly_issues(self) -> List[Issue]:
        deadly_issues = []
        for issue in self.issues:
            if issue.deadly:
                deadly_issues.append(issue)

        if not deadly_issues:
            raise NoDeadlyIssueError()
        return deadly_issues

    def get_deadly_issue_reasons(self) -> str:
        issues = self.get_deadly_issues()
        reasons = [x.description for x in issues]
        return "; ".join(reasons)

    def set_unhealthy(self, issues: List[Issue]):
        self.healthy = False
        self.issues = issues


@dataclass
class DiagnosisList:
    diagnoses: List[Diagnosis]

    def is_death(self) -> bool:
        """if any core probe give not death diagnosis"""
        for diagnosis in self.diagnoses:
            if diagnosis.is_core and not diagnosis.alive:
                return True

        return False

    def get_death_report(self) -> dict:
        if not self.is_death():
            raise ValueError("there is not death report")

        return {x.system_name: x.get_deadly_issue_reasons() for x in self.diagnoses if x.is_core and not x.alive}


class VirtualProbe:
    """virtual probe"""

    name: str = ""
    is_core = True

    def __init__(self):
        self.diagnosis = Diagnosis(system_name=self.name, is_core=self.is_core)

    def diagnose(self) -> Diagnosis:
        raise NotImplementedError


class HttpProbe(VirtualProbe):
    """http Probe"""

    # For most simple http-service probe could change the `simple_diagnose`
    # without diagnose logic duplicated
    simple_diagnose: Dict = {}

    healthz_check: Dict = {}
    # probe could choose method, make a healthz check if `/healthz` api exists
    diagnose_method = "make_simple_request"

    def make_simple_request(self):
        """get request to simple diagnose url"""
        try:
            result = requests.get(self.simple_diagnose["url"], timeout=5)
        except KeyError:
            raise ValueError("probe has to fulfill the simple diagnose config before use it")

        if result.status_code != self.simple_diagnose.get("status_code", 200):
            raise StatusMissError(result.status_code, self.simple_diagnose.get("status_code"))

    def make_healthz_check(self):
        """only suit for internal projects which has a format `healthz` output"""
        try:
            result = requests.get(
                url=self.healthz_check["url"],
                params={"token": self.healthz_check["token"]},
                timeout=5,
            )
        except KeyError:
            raise ValueError("probe has to fulfill the simple diagnose config before use it")

        if result.status_code != 200:
            message = result.text[:512] if result.text else ""
            raise SystemNotHealthyError(system_name=self.name, message=message)
        # if not result.json().get("result"):
        #     raise SystemNotHealthyError(system_name=self.name, message=result.json().get("message"))

    def diagnose(self) -> Diagnosis:
        try:
            getattr(self, self.diagnose_method)()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("diagnose http endpoint failed")
            deadly_issue = Issue(deadly=True, description=str(e))
            self.diagnosis.set_dead([deadly_issue])

        return self.diagnosis


class TCPProbe(VirtualProbe):
    def diagnose(self) -> Diagnosis:
        raise NotImplementedError


class RedisProbe(TCPProbe):
    redis_url = ""

    def diagnose(self) -> Diagnosis:
        if not self.redis_url:
            raise ValueError("should provide redis url")
        try:
            # from_url already used connection pool
            connection = redis.Redis.from_url(self.redis_url)
            connection.ping()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("diagnose redis endpoint failed")
            deadly_issue = Issue(deadly=True, description=str(e))
            self.diagnosis.set_dead([deadly_issue])

        return self.diagnosis


class MySQLProbe(TCPProbe):
    mysql_config: Dict = {}

    def diagnose(self) -> Diagnosis:
        try:
            connection = pymysql.connect(**self.mysql_config)
        except KeyError:
            logger.exception(f"db<{self.name}> conf is not complete")
            issue = Issue(deadly=True, description=f"db<{self.name}> conf is not complete")
            self.diagnosis.set_dead([issue])
            return self.diagnosis

        try:
            with connection.cursor() as cursor:
                sql = "SELECT 1"
                cursor.execute(sql)

            connection.commit()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("diagnose mysql endpoint failed")
            issue = Issue(deadly=True, description=f"connection to mysql<{self.name}> failed: {e}")
            self.diagnosis.set_dead([issue])

        finally:
            connection.close()

        return self.diagnosis


@dataclass
class ProbeSet:
    # a ProbeSet has to own one probe at least
    probes: List[Type[VirtualProbe]]

    def examination(self) -> DiagnosisList:
        diagnosis_list = []
        for probe_cls in self.probes:
            diagnosis_list.append(probe_cls().diagnose())
        return DiagnosisList(diagnosis_list)
