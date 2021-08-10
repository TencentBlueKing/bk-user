{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "chartty.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "chartty.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "chartty.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "chartty.labels" -}}
helm.sh/chart: {{ include "chartty.chart" . }}
{{- with .Values.podLabels }}
{{ toYaml . }}
{{- end }}
{{ include "chartty.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "chartty.selectorLabels" -}}
app.kubernetes.io/name: {{ include "chartty.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "chartty.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "chartty.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/* Create the docker config json for image pull secret */}}
{{- define "chartty.dockerconfigjson" -}}
{{- with .Values.global.imageCredentials }}
{{- printf "{\"auths\":{\"%s\":{\"username\":\"%s\",\"password\":\"%s\",\"auth\":\"%s\"}}}" .registry .username .password (printf "%s:%s" .username .password | b64enc) | b64enc }}
{{- end }}
{{- end }}

{{/* Create imageSerect fields */}}
{{- define "chartty.imagePullSecretNames" -}}
{{- if .Values.global.imageCredentials.enabled -}}
- name: {{ include "chartty.name" . }}-{{ default "dockerconfigjson" .Values.global.imageCredentials.name }}
{{- range $value := .Values.global.imagePullSecrets }}
- name: {{ $value }}
{{- end }}
{{- else }}
{{- if .Values.global.imagePullSecrets }}
{{- range $value := .Values.global.imagePullSecrets }}
- name: {{ $value }}
{{- end }}
{{- else }}[]
{{- end }}
{{- end }}
{{- end }}

{{/* Create envs */}}
{{- define "chartty.envs" -}}
{{- with .Values.extrasEnv }}
{{- /* 直接渲染 extrasEnv */ -}}
{{- toYaml . }}
{{- end }}
{{- /* 渲染 sharedUrlEnvMap */ -}}
{{- range $k, $v := .Values.sharedUrlEnvMap }}
{{- if hasKey $.Values.env $k }}
{{- else }}
- name: {{ $k }}
  value: "{{ tpl $v $ }}"
{{- end }}
{{- end }}
{{- /* 渲染 global 环境变量时，如果模块已指定直接跳过 */ -}}
{{- range $k, $v := .Values.global.env }}
{{- if hasKey $.Values.env $k }}
{{- else }}
- name: {{ $k }}
  value: "{{ $v }}"
{{- end }}
{{- end }}
{{- /* 高优先级渲染 .Values.env */ -}}
{{- range $k, $v := .Values.env }}
- name: {{ $k }}
  value: "{{ $v }}"
{{- end }}
{{- end }}