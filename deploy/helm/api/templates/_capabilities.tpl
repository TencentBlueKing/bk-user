{{/* vim: set filetype=mustache: */}}

{{/*
Return the target Kubernetes version
*/}}
{{- define "chartty.capabilities.kubeVersion" -}}
{{- .Values.global.kubeVersion | default .Capabilities.KubeVersion.Version -}}
{{- end -}}

{{/*
Return the appropriate apiVersion for policy.
*/}}
{{- define "chartty.capabilities.policy.apiVersion" -}}
{{- if semverCompare "<1.21-0" (include "chartty.capabilities.kubeVersion" .) -}}
{{- print "policy/v1beta1" -}}
{{- else -}}
{{- print "policy/v1" -}}
{{- end -}}
{{- end -}}

{{/*
Return the appropriate apiVersion for cronjob.
*/}}
{{- define "chartty.capabilities.cronjob.apiVersion" -}}
{{- if semverCompare "<1.21-0" (include "chartty.capabilities.kubeVersion" .) -}}
{{- print "batch/v1beta1" -}}
{{- else -}}
{{- print "batch/v1" -}}
{{- end -}}
{{- end -}}

{{/*
Return the appropriate apiVersion for deployment.
*/}}
{{- define "chartty.capabilities.deployment.apiVersion" -}}
{{- if semverCompare "<1.14-0" (include "chartty.capabilities.kubeVersion" .) -}}
{{- print "extensions/v1beta1" -}}
{{- else -}}
{{- print "apps/v1" -}}
{{- end -}}
{{- end -}}

{{/*
Return the appropriate apiVersion for statefulset.
*/}}
{{- define "chartty.capabilities.statefulset.apiVersion" -}}
{{- if semverCompare "<1.14-0" (include "chartty.capabilities.kubeVersion" .) -}}
{{- print "apps/v1beta1" -}}
{{- else -}}
{{- print "apps/v1" -}}
{{- end -}}
{{- end -}}

{{/*
Return the appropriate apiVersion for ingress.
*/}}
{{- define "chartty.capabilities.ingress.apiVersion" -}}
{{- if semverCompare "<1.14-0" (include "chartty.capabilities.kubeVersion" .) -}}
{{- print "extensions/v1beta1" -}}
{{- else if semverCompare "<1.19-0" (include "chartty.capabilities.kubeVersion" .) -}}
{{- print "networking.k8s.io/v1beta1" -}}
{{- else -}}
{{- print "networking.k8s.io/v1" -}}
{{- end }}
{{- end -}}

{{/*
Return the appropriate apiVersion for RBAC resources.
*/}}
{{- define "chartty.capabilities.rbac.apiVersion" -}}
{{- if semverCompare "<1.17-0" (include "chartty.capabilities.kubeVersion" .) -}}
{{- print "rbac.authorization.k8s.io/v1beta1" -}}
{{- else -}}
{{- print "rbac.authorization.k8s.io/v1" -}}
{{- end -}}
{{- end -}}

{{/*
Return the appropriate apiVersion for CRDs.
*/}}
{{- define "chartty.capabilities.crd.apiVersion" -}}
{{- if semverCompare "<1.19-0" (include "chartty.capabilities.kubeVersion" .) -}}
{{- print "apiextensions.k8s.io/v1beta1" -}}
{{- else -}}
{{- print "apiextensions.k8s.io/v1" -}}
{{- end -}}
{{- end -}}

{{/*
Returns true if the used Helm version is 3.3+.
A way to check the used Helm version was not introduced until version 3.3.0 with .Capabilities.HelmVersion, which contains an additional "{}}"  structure.
This check is introduced as a regexMatch instead of {{ if .Capabilities.HelmVersion }} because checking for the key HelmVersion in <3.3 results in a "interface not found" error.
**To be removed when the catalog's minimun Helm version is 3.3**
*/}}
{{- define "chartty.capabilities.supportsHelmVersion" -}}
{{- if regexMatch "{(v[0-9])*[^}]*}}$" (.Capabilities | toString ) }}
  {{- true -}}
{{- end -}}
{{- end -}}