{{/*
Shortcuts for redis
*/}}
{{- define "bk-user.apiExternalRedisBrokerUrl" -}}
{{- printf "redis://:%s@%s:%s/0" .Values.api.externalRedis.default.password .Values.api.externalRedis.default.host (.Values.api.externalRedis.default.port | toString )}}
{{- end }}

{{- define "bk-user.builtinRedisBrokerUrl" -}}
{{- printf "redis://:%s@%s-redis-master:%s/0" .Values.redis.auth.password .Release.Name (.Values.redis.master.service.port | toString )}}
{{- end }}
