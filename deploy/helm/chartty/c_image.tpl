{{/* vim: set filetype=mustache: */}}

{{/* Create image */}}
{{- define "chartty.image" -}}
"{{ .Values.image.registry | default .Values.global.sharedImageRegistry }}/{{ required ".Values.image.repository is required" .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
{{- end }}