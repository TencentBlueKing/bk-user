{{/* vim: set filetype=mustache: */}}

{{/* Create image */}}
{{- define "chartty.image" -}}
"{{ .Values.global.image.registry }}/{{ .Values.image.name }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
{{- end }}