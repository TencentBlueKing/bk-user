version ?= "v2.3.0"
values ?=
image_repo ?= "ccr.ccs.tencentyun.com/bk.io"
chart_repo ?=

generate-release-md:
	cd src/saas/ && poetry run python manage.py generate_release_md > release.md
	mv src/saas/release.md docs/

link:
	ln -s ${PWD}/src/bkuser_global src/api || true
	ln -s ${PWD}/src/bkuser_global src/saas || true
	ln -s ${PWD}/src/sdk/bkuser_sdk src/saas || true

generate-sdk:
	cd src/ && swagger-codegen generate -i http://localhost:8004/redoc/\?format\=openapi -l python -o sdk/ -c config.json

build-api:
	docker build -f src/api/Dockerfile . -t ${image_repo}/bk.io/bk-user-api:${version}

build-saas:
	docker build -f src/saas/Dockerfile . -t ${image_repo}/bk.io/bk-user-saas:${version}

build-all: build-api build-saas

push:
	docker push ${image_repo}/bk.io/bk-user-api:${version}
	docker push ${image_repo}/bk.io/bk-user-saas:${version}

helm-sync:
	ln -s ${PWD}/deploy/helm/chartty/* deploy/helm/api/templates/ || true
	ln -s ${PWD}/deploy/helm/chartty/* deploy/helm/saas/templates/ || true

helm-refresh: helm-sync
	cd deploy/helm && helm dependency update bk-user-stack --skip-refresh

helm-debug: helm-refresh
	cd deploy/helm && helm install bk-user-test bk-user-stack --debug --dry-run -f local_values.yaml

helm-install: helm-refresh
	kubectl create ns bk-user || true
	cd deploy/helm && helm install bk-user-test bk-user-stack --namespace bk-user -f local_values.yaml

helm-upgrade: helm-refresh
	cd deploy/helm && helm upgrade bk-user-test bk-user-stack -n bk-user -f local_values.yaml

helm-uninstall:
	helm uninstall bk-user-test -n bk-user
	kubectl delete ns bk-user

helm-package: helm-refresh
	cd deploy/helm && helm package bk-user-stack -d dist/

helm-publish: deploy/helm/dist/*.tgz
	for f in $^; do \
		curl -kL -X POST -F chart=@$${f} -u ${credentials} ${chart_repo}; \
	done