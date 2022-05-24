{{/*
Shortcuts for redis
*/}}
{{- define "bk-user.externalRedisBrokerUrl" -}}
{{- printf "redis://:%s@%s:%s/0" .Values.externalRedis.default.password .Values.externalRedis.default.host (.Values.externalRedis.default.port | toString )}}
{{- end }}
