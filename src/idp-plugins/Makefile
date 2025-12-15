help: ## 展示可用 make 命令及说明
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


package-idp-plugin: ## 打包自定义 IDP 插件
	@if [ -z "$(name)" ]; then \
		echo "Error: name parameter is required. Usage: make package-idp-plugin name=<plugin_directory_name>"; \
		exit 1; \
	fi
	@configmap_name=bk-user-idp-plugin-$(shell echo ${name} | sed 's/_/-/g'); \
	kubectl create configmap $${configmap_name} --from-file=idp_plugins/${name} --dry-run=client -o yaml > $${configmap_name}.yaml
