(function webpackUniversalModuleDefinition(root, factory) {
  if (typeof exports === 'object' && typeof module === 'object') module.exports = factory(require('vue'));
  else if (typeof define === 'function' && define.amd) define(['vue'], factory);
  else if (typeof exports === 'object') exports.bkSchemaForm = factory(require('vue'));
  else root.bkSchemaForm = factory(root.vue);
}((typeof self !== 'undefined' ? self : this), __WEBPACK_EXTERNAL_MODULE__748__ =>
/** ****/ (function () { // webpackBootstrap
    /** ****/ 	const __webpack_modules__ = ({

      /***/ 6870:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.formatNames = exports.fastFormats = exports.fullFormats = void 0;
        function fmtDef(validate, compare) {
          return { validate, compare };
        }
        exports.fullFormats = {
          // date: http://tools.ietf.org/html/rfc3339#section-5.6
          date: fmtDef(date, compareDate),
          // date-time: http://tools.ietf.org/html/rfc3339#section-5.6
          time: fmtDef(time, compareTime),
          'date-time': fmtDef(date_time, compareDateTime),
          // duration: https://tools.ietf.org/html/rfc3339#appendix-A
          duration: /^P(?!$)((\d+Y)?(\d+M)?(\d+D)?(T(?=\d)(\d+H)?(\d+M)?(\d+S)?)?|(\d+W)?)$/,
          uri,
          'uri-reference': /^(?:[a-z][a-z0-9+\-.]*:)?(?:\/?\/(?:(?:[a-z0-9\-._~!$&'()*+,;=:]|%[0-9a-f]{2})*@)?(?:\[(?:(?:(?:(?:[0-9a-f]{1,4}:){6}|::(?:[0-9a-f]{1,4}:){5}|(?:[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){4}|(?:(?:[0-9a-f]{1,4}:){0,1}[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){3}|(?:(?:[0-9a-f]{1,4}:){0,2}[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){2}|(?:(?:[0-9a-f]{1,4}:){0,3}[0-9a-f]{1,4})?::[0-9a-f]{1,4}:|(?:(?:[0-9a-f]{1,4}:){0,4}[0-9a-f]{1,4})?::)(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))|(?:(?:[0-9a-f]{1,4}:){0,5}[0-9a-f]{1,4})?::[0-9a-f]{1,4}|(?:(?:[0-9a-f]{1,4}:){0,6}[0-9a-f]{1,4})?::)|[Vv][0-9a-f]+\.[a-z0-9\-._~!$&'()*+,;=:]+)\]|(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)|(?:[a-z0-9\-._~!$&'"()*+,;=]|%[0-9a-f]{2})*)(?::\d*)?(?:\/(?:[a-z0-9\-._~!$&'"()*+,;=:@]|%[0-9a-f]{2})*)*|\/(?:(?:[a-z0-9\-._~!$&'"()*+,;=:@]|%[0-9a-f]{2})+(?:\/(?:[a-z0-9\-._~!$&'"()*+,;=:@]|%[0-9a-f]{2})*)*)?|(?:[a-z0-9\-._~!$&'"()*+,;=:@]|%[0-9a-f]{2})+(?:\/(?:[a-z0-9\-._~!$&'"()*+,;=:@]|%[0-9a-f]{2})*)*)?(?:\?(?:[a-z0-9\-._~!$&'"()*+,;=:@/?]|%[0-9a-f]{2})*)?(?:#(?:[a-z0-9\-._~!$&'"()*+,;=:@/?]|%[0-9a-f]{2})*)?$/i,
          // uri-template: https://tools.ietf.org/html/rfc6570
          'uri-template': /^(?:(?:[^\x00-\x20"'<>%\\^`{|}]|%[0-9a-f]{2})|\{[+#./;?&=,!@|]?(?:[a-z0-9_]|%[0-9a-f]{2})+(?::[1-9][0-9]{0,3}|\*)?(?:,(?:[a-z0-9_]|%[0-9a-f]{2})+(?::[1-9][0-9]{0,3}|\*)?)*\})*$/i,
          // For the source: https://gist.github.com/dperini/729294
          // For test cases: https://mathiasbynens.be/demo/url-regex
          url: /^(?:https?|ftp):\/\/(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z0-9\u{00a1}-\u{ffff}]+-)*[a-z0-9\u{00a1}-\u{ffff}]+)(?:\.(?:[a-z0-9\u{00a1}-\u{ffff}]+-)*[a-z0-9\u{00a1}-\u{ffff}]+)*(?:\.(?:[a-z\u{00a1}-\u{ffff}]{2,})))(?::\d{2,5})?(?:\/[^\s]*)?$/iu,
          email: /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/i,
          hostname: /^(?=.{1,253}\.?$)[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[-0-9a-z]{0,61}[0-9a-z])?)*\.?$/i,
          // optimized https://www.safaribooksonline.com/library/view/regular-expressions-cookbook/9780596802837/ch07s16.html
          ipv4: /^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$/,
          ipv6: /^((([0-9a-f]{1,4}:){7}([0-9a-f]{1,4}|:))|(([0-9a-f]{1,4}:){6}(:[0-9a-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9a-f]{1,4}:){5}(((:[0-9a-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9a-f]{1,4}:){4}(((:[0-9a-f]{1,4}){1,3})|((:[0-9a-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){3}(((:[0-9a-f]{1,4}){1,4})|((:[0-9a-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){2}(((:[0-9a-f]{1,4}){1,5})|((:[0-9a-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){1}(((:[0-9a-f]{1,4}){1,6})|((:[0-9a-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9a-f]{1,4}){1,7})|((:[0-9a-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))$/i,
          regex,
          // uuid: http://tools.ietf.org/html/rfc4122
          uuid: /^(?:urn:uuid:)?[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i,
          // JSON-pointer: https://tools.ietf.org/html/rfc6901
          // uri fragment: https://tools.ietf.org/html/rfc3986#appendix-A
          'json-pointer': /^(?:\/(?:[^~/]|~0|~1)*)*$/,
          'json-pointer-uri-fragment': /^#(?:\/(?:[a-z0-9_\-.!$&'()*+,;:=@]|%[0-9a-f]{2}|~0|~1)*)*$/i,
          // relative JSON-pointer: http://tools.ietf.org/html/draft-luff-relative-json-pointer-00
          'relative-json-pointer': /^(?:0|[1-9][0-9]*)(?:#|(?:\/(?:[^~/]|~0|~1)*)*)$/,
          // the following formats are used by the openapi specification: https://spec.openapis.org/oas/v3.0.0#data-types
          // byte: https://github.com/miguelmota/is-base64
          byte,
          // signed 32 bit integer
          int32: { type: 'number', validate: validateInt32 },
          // signed 64 bit integer
          int64: { type: 'number', validate: validateInt64 },
          // C-type float
          float: { type: 'number', validate: validateNumber },
          // C-type double
          double: { type: 'number', validate: validateNumber },
          // hint to the UI to hide input strings
          password: true,
          // unchecked string payload
          binary: true,
        };
        exports.fastFormats = {
          ...exports.fullFormats,
          date: fmtDef(/^\d\d\d\d-[0-1]\d-[0-3]\d$/, compareDate),
          time: fmtDef(/^(?:[0-2]\d:[0-5]\d:[0-5]\d|23:59:60)(?:\.\d+)?(?:z|[+-]\d\d(?::?\d\d)?)?$/i, compareTime),
          'date-time': fmtDef(/^\d\d\d\d-[0-1]\d-[0-3]\d[t\s](?:[0-2]\d:[0-5]\d:[0-5]\d|23:59:60)(?:\.\d+)?(?:z|[+-]\d\d(?::?\d\d)?)$/i, compareDateTime),
          // uri: https://github.com/mafintosh/is-my-json-valid/blob/master/formats.js
          uri: /^(?:[a-z][a-z0-9+\-.]*:)(?:\/?\/)?[^\s]*$/i,
          'uri-reference': /^(?:(?:[a-z][a-z0-9+\-.]*:)?\/?\/)?(?:[^\\\s#][^\s#]*)?(?:#[^\\\s]*)?$/i,
          // email (sources from jsen validator):
          // http://stackoverflow.com/questions/201323/using-a-regular-expression-to-validate-an-email-address#answer-8829363
          // http://www.w3.org/TR/html5/forms.html#valid-e-mail-address (search for 'wilful violation')
          email: /^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*$/i,
        };
        exports.formatNames = Object.keys(exports.fullFormats);
        function isLeapYear(year) {
          // https://tools.ietf.org/html/rfc3339#appendix-C
          return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
        }
        const DATE = /^(\d\d\d\d)-(\d\d)-(\d\d)$/;
        const DAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        function date(str) {
          // full-date from http://tools.ietf.org/html/rfc3339#section-5.6
          const matches = DATE.exec(str);
          if (!matches) return false;
          const year = +matches[1];
          const month = +matches[2];
          const day = +matches[3];
          return (month >= 1
        && month <= 12
        && day >= 1
        && day <= (month === 2 && isLeapYear(year) ? 29 : DAYS[month]));
        }
        function compareDate(d1, d2) {
          if (!(d1 && d2)) return undefined;
          if (d1 > d2) return 1;
          if (d1 < d2) return -1;
          return 0;
        }
        const TIME = /^(\d\d):(\d\d):(\d\d)(\.\d+)?(z|[+-]\d\d(?::?\d\d)?)?$/i;
        function time(str, withTimeZone) {
          const matches = TIME.exec(str);
          if (!matches) return false;
          const hour = +matches[1];
          const minute = +matches[2];
          const second = +matches[3];
          const timeZone = matches[5];
          return (((hour <= 23 && minute <= 59 && second <= 59)
        || (hour === 23 && minute === 59 && second === 60))
        && (!withTimeZone || timeZone !== ''));
        }
        function compareTime(t1, t2) {
          if (!(t1 && t2)) return undefined;
          const a1 = TIME.exec(t1);
          const a2 = TIME.exec(t2);
          if (!(a1 && a2)) return undefined;
          t1 = a1[1] + a1[2] + a1[3] + (a1[4] || '');
          t2 = a2[1] + a2[2] + a2[3] + (a2[4] || '');
          if (t1 > t2) return 1;
          if (t1 < t2) return -1;
          return 0;
        }
        const DATE_TIME_SEPARATOR = /t|\s/i;
        function date_time(str) {
          // http://tools.ietf.org/html/rfc3339#section-5.6
          const dateTime = str.split(DATE_TIME_SEPARATOR);
          return dateTime.length === 2 && date(dateTime[0]) && time(dateTime[1], true);
        }
        function compareDateTime(dt1, dt2) {
          if (!(dt1 && dt2)) return undefined;
          const [d1, t1] = dt1.split(DATE_TIME_SEPARATOR);
          const [d2, t2] = dt2.split(DATE_TIME_SEPARATOR);
          const res = compareDate(d1, d2);
          if (res === undefined) return undefined;
          return res || compareTime(t1, t2);
        }
        const NOT_URI_FRAGMENT = /\/|:/;
        const URI = /^(?:[a-z][a-z0-9+\-.]*:)(?:\/?\/(?:(?:[a-z0-9\-._~!$&'()*+,;=:]|%[0-9a-f]{2})*@)?(?:\[(?:(?:(?:(?:[0-9a-f]{1,4}:){6}|::(?:[0-9a-f]{1,4}:){5}|(?:[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){4}|(?:(?:[0-9a-f]{1,4}:){0,1}[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){3}|(?:(?:[0-9a-f]{1,4}:){0,2}[0-9a-f]{1,4})?::(?:[0-9a-f]{1,4}:){2}|(?:(?:[0-9a-f]{1,4}:){0,3}[0-9a-f]{1,4})?::[0-9a-f]{1,4}:|(?:(?:[0-9a-f]{1,4}:){0,4}[0-9a-f]{1,4})?::)(?:[0-9a-f]{1,4}:[0-9a-f]{1,4}|(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))|(?:(?:[0-9a-f]{1,4}:){0,5}[0-9a-f]{1,4})?::[0-9a-f]{1,4}|(?:(?:[0-9a-f]{1,4}:){0,6}[0-9a-f]{1,4})?::)|[Vv][0-9a-f]+\.[a-z0-9\-._~!$&'()*+,;=:]+)\]|(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)|(?:[a-z0-9\-._~!$&'()*+,;=]|%[0-9a-f]{2})*)(?::\d*)?(?:\/(?:[a-z0-9\-._~!$&'()*+,;=:@]|%[0-9a-f]{2})*)*|\/(?:(?:[a-z0-9\-._~!$&'()*+,;=:@]|%[0-9a-f]{2})+(?:\/(?:[a-z0-9\-._~!$&'()*+,;=:@]|%[0-9a-f]{2})*)*)?|(?:[a-z0-9\-._~!$&'()*+,;=:@]|%[0-9a-f]{2})+(?:\/(?:[a-z0-9\-._~!$&'()*+,;=:@]|%[0-9a-f]{2})*)*)(?:\?(?:[a-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9a-f]{2})*)?(?:#(?:[a-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9a-f]{2})*)?$/i;
        function uri(str) {
          // http://jmrware.com/articles/2009/uri_regexp/URI_regex.html + optional protocol + required "."
          return NOT_URI_FRAGMENT.test(str) && URI.test(str);
        }
        const BYTE = /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/gm;
        function byte(str) {
          BYTE.lastIndex = 0;
          return BYTE.test(str);
        }
        const MIN_INT32 = -(2 ** 31);
        const MAX_INT32 = 2 ** 31 - 1;
        function validateInt32(value) {
          return Number.isInteger(value) && value <= MAX_INT32 && value >= MIN_INT32;
        }
        function validateInt64(value) {
          // JSON and javascript max Int is 2**53, so any int that passes isInteger is valid for Int64
          return Number.isInteger(value);
        }
        function validateNumber() {
          return true;
        }
        const Z_ANCHOR = /[^\\]\\Z/;
        function regex(str) {
          if (Z_ANCHOR.test(str)) return false;
          try {
            new RegExp(str);
            return true;
          } catch (e) {
            return false;
          }
        }
        // # sourceMappingURL=formats.js.map
        /***/ }),

      /***/ 5477:
      /***/ (function (module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const formats_1 = __webpack_require__(6870);
        const limit_1 = __webpack_require__(7963);
        const codegen_1 = __webpack_require__(3487);
        const fullName = new codegen_1.Name('fullFormats');
        const fastName = new codegen_1.Name('fastFormats');
        const formatsPlugin = (ajv, opts = { keywords: true }) => {
          if (Array.isArray(opts)) {
            addFormats(ajv, opts, formats_1.fullFormats, fullName);
            return ajv;
          }
          const [formats, exportName] = opts.mode === 'fast' ? [formats_1.fastFormats, fastName] : [formats_1.fullFormats, fullName];
          const list = opts.formats || formats_1.formatNames;
          addFormats(ajv, list, formats, exportName);
          if (opts.keywords) limit_1.default(ajv);
          return ajv;
        };
        formatsPlugin.get = (name, mode = 'full') => {
          const formats = mode === 'fast' ? formats_1.fastFormats : formats_1.fullFormats;
          const f = formats[name];
          if (!f) throw new Error(`Unknown format "${name}"`);
          return f;
        };
        function addFormats(ajv, list, fs, exportName) {
          let _a;
          let _b;
          (_a = (_b = ajv.opts.code).formats) !== null && _a !== void 0 ? _a : (_b.formats = codegen_1._ `require("ajv-formats/dist/formats").${exportName}`);
          for (const f of list) ajv.addFormat(f, fs[f]);
        }
        module.exports = exports = formatsPlugin;
        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.default = formatsPlugin;
        // # sourceMappingURL=index.js.map
        /***/ }),

      /***/ 7963:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.formatLimitDefinition = void 0;
        const ajv_1 = __webpack_require__(1581);
        const codegen_1 = __webpack_require__(3487);
        const ops = codegen_1.operators;
        const KWDs = {
          formatMaximum: { okStr: '<=', ok: ops.LTE, fail: ops.GT },
          formatMinimum: { okStr: '>=', ok: ops.GTE, fail: ops.LT },
          formatExclusiveMaximum: { okStr: '<', ok: ops.LT, fail: ops.GTE },
          formatExclusiveMinimum: { okStr: '>', ok: ops.GT, fail: ops.LTE },
        };
        const error = {
          message: ({ keyword, schemaCode }) => codegen_1.str `should be ${KWDs[keyword].okStr} ${schemaCode}`,
          params: ({ keyword, schemaCode }) => codegen_1._ `{comparison: ${KWDs[keyword].okStr}, limit: ${schemaCode}}`,
        };
        exports.formatLimitDefinition = {
          keyword: Object.keys(KWDs),
          type: 'string',
          schemaType: 'string',
          $data: true,
          error,
          code(cxt) {
            const { gen, data, schemaCode, keyword, it } = cxt;
            const { opts, self } = it;
            if (!opts.validateFormats) return;
            const fCxt = new ajv_1.KeywordCxt(it, self.RULES.all.format.definition, 'format');
            if (fCxt.$data) validate$DataFormat();
            else validateFormat();
            function validate$DataFormat() {
              const fmts = gen.scopeValue('formats', {
                ref: self.formats,
                code: opts.code.formats,
              });
              const fmt = gen.const('fmt', codegen_1._ `${fmts}[${fCxt.schemaCode}]`);
              cxt.fail$data(codegen_1.or(codegen_1._ `typeof ${fmt} != "object"`, codegen_1._ `${fmt} instanceof RegExp`, codegen_1._ `typeof ${fmt}.compare != "function"`, compareCode(fmt)));
            }
            function validateFormat() {
              const format = fCxt.schema;
              const fmtDef = self.formats[format];
              if (!fmtDef || fmtDef === true) return;
              if (typeof fmtDef !== 'object'
                || fmtDef instanceof RegExp
                || typeof fmtDef.compare !== 'function') {
                throw new Error(`"${keyword}": format "${format}" does not define "compare" function`);
              }
              const fmt = gen.scopeValue('formats', {
                key: format,
                ref: fmtDef,
                code: opts.code.formats ? codegen_1._ `${opts.code.formats}${codegen_1.getProperty(format)}` : undefined,
              });
              cxt.fail$data(compareCode(fmt));
            }
            function compareCode(fmt) {
              return codegen_1._ `${fmt}.compare(${data}, ${schemaCode}) ${KWDs[keyword].fail} 0`;
            }
          },
          dependencies: ['format'],
        };
        const formatLimitPlugin = (ajv) => {
          ajv.addKeyword(exports.formatLimitDefinition);
          return ajv;
        };
        exports.default = formatLimitPlugin;
        // # sourceMappingURL=limit.js.map
        /***/ }),

      /***/ 6366:
      /***/ (function (module) {
        'use strict';

        module.exports = function localize_zh(errors) {
          if (!(errors && errors.length)) return;
          for (const e of errors) {
            let out;
            switch (e.keyword) {
              case 'additionalItems':
              case 'items':
                out = '';
                var n = e.params.limit;
                out += `不允许超过${n}个元素`;
                break;
              case 'additionalProperties':
                out = '不允许有额外的属性';
                break;
              case 'anyOf':
                out = '数据应为 anyOf 所指定的其中一个';
                break;
              case 'const':
                out = '应当等于常量';
                break;
              case 'contains':
                out = '应当包含一个有效项';
                break;
              case 'dependencies':
              case 'dependentRequired':
                out = '';
                var n = e.params.depsCount;
                out += `应当拥有属性${e.params.property}的依赖属性${e.params.deps}`;
                break;
              case 'discriminator':
                switch (e.params.error) {
                  case 'tag':
                    out = `标签 "${e.params.tag}" 的类型必须为字符串`;
                    break;
                  case 'mapping':
                    out = `标签 "${e.params.tag}" 的值必须在 oneOf 之中`;
                    break;
                  default:
                    out = `应当通过 "${e.keyword} 关键词校验"`;
                }
                break;
              case 'enum':
                out = '应当是预设定的枚举值之一';
                break;
              case 'false schema':
                out = '布尔模式出错';
                break;
              case 'format':
                out = `应当匹配格式 "${e.params.format}"`;
                break;
              case 'formatMaximum':
              case 'formatExclusiveMaximum':
                out = '';
                var cond = `${e.params.comparison} ${e.params.limit}`;
                out += `应当是 ${cond}`;
                break;
              case 'formatMinimum':
              case 'formatExclusiveMinimum':
                out = '';
                var cond = `${e.params.comparison} ${e.params.limit}`;
                out += `应当是 ${cond}`;
                break;
              case 'if':
                out = `应当匹配模式 "${e.params.failingKeyword}" `;
                break;
              case 'maximum':
              case 'exclusiveMaximum':
                out = '';
                var cond = `${e.params.comparison} ${e.params.limit}`;
                out += `应当为 ${cond}`;
                break;
              case 'maxItems':
                out = '';
                var n = e.params.limit;
                out += `不应多于 ${n} 个项`;
                break;
              case 'maxLength':
                out = '';
                var n = e.params.limit;
                out += `不应多于 ${n} 个字符`;
                break;
              case 'maxProperties':
                out = '';
                var n = e.params.limit;
                out += `不应有多于 ${n} 个属性`;
                break;
              case 'minimum':
              case 'exclusiveMinimum':
                out = '';
                var cond = `${e.params.comparison} ${e.params.limit}`;
                out += `应当为 ${cond}`;
                break;
              case 'minItems':
                out = '';
                var n = e.params.limit;
                out += `不应少于 ${n} 个项`;
                break;
              case 'minLength':
                out = '';
                var n = e.params.limit;
                out += `不应少于 ${n} 个字符`;
                break;
              case 'minProperties':
                out = '';
                var n = e.params.limit;
                out += `不应有少于 ${n} 个属性`;
                break;
              case 'multipleOf':
                out = `应当是 ${e.params.multipleOf} 的整数倍`;
                break;
              case 'not':
                out = '不应当匹配 "not" schema';
                break;
              case 'oneOf':
                out = '只能匹配一个 "oneOf" 中的 schema';
                break;
              case 'pattern':
                out = `应当匹配模式 "${e.params.pattern}"`;
                break;
              case 'patternRequired':
                out = `应当有属性匹配模式 ${e.params.missingPattern}`;
                break;
              case 'propertyNames':
                out = '属性名 无效';
                break;
              case 'required':
                out = `应当有必需属性 ${e.params.missingProperty}`;
                break;
              case 'type':
                out = `应当是 ${e.params.type} 类型`;
                break;
              case 'unevaluatedItems':
                out = '';
                var n = e.params.len;
                out += ` 不允许有超过 ${n} 个元素`;
                break;
              case 'unevaluatedProperties':
                out = '不允许存在未求值的属性';
                break;
              case 'uniqueItems':
                out =          `不应当含有重复项 (第 ${
                  e.params.j
                } 项与第 ${
                  e.params.i
                } 项是重复的)`;
                break;
              default:
                out = `应当通过 "${e.keyword} 关键词校验"`;
            }
            e.message = out;
          }
        };
        /***/ }),

      /***/ 1581:
      /***/ (function (module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.MissingRefError = exports.ValidationError = exports.CodeGen = exports.Name = exports.nil = exports.stringify = exports.str = exports._ = exports.KeywordCxt = void 0;
        const core_1 = __webpack_require__(7159);
        const draft7_1 = __webpack_require__(3924);
        const discriminator_1 = __webpack_require__(1240);
        const draft7MetaSchema = __webpack_require__(98);
        const META_SUPPORT_DATA = ['/properties'];
        const META_SCHEMA_ID = 'http://json-schema.org/draft-07/schema';
        class Ajv extends core_1.default {
          _addVocabularies() {
            super._addVocabularies();
            draft7_1.default.forEach(v => this.addVocabulary(v));
            if (this.opts.discriminator) this.addKeyword(discriminator_1.default);
          }
          _addDefaultMetaSchema() {
            super._addDefaultMetaSchema();
            if (!this.opts.meta) return;
            const metaSchema = this.opts.$data
              ? this.$dataMetaSchema(draft7MetaSchema, META_SUPPORT_DATA)
              : draft7MetaSchema;
            this.addMetaSchema(metaSchema, META_SCHEMA_ID, false);
            this.refs['http://json-schema.org/schema'] = META_SCHEMA_ID;
          }
          defaultMeta() {
            return (this.opts.defaultMeta =            super.defaultMeta() || (this.getSchema(META_SCHEMA_ID) ? META_SCHEMA_ID : undefined));
          }
        }
        module.exports = exports = Ajv;
        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.default = Ajv;
        const validate_1 = __webpack_require__(4815);
        Object.defineProperty(exports, 'KeywordCxt', ({ enumerable: true, get() {
          return validate_1.KeywordCxt;
        } }));
        const codegen_1 = __webpack_require__(3487);
        Object.defineProperty(exports, '_', ({ enumerable: true, get() {
          return codegen_1._;
        } }));
        Object.defineProperty(exports, 'str', ({ enumerable: true, get() {
          return codegen_1.str;
        } }));
        Object.defineProperty(exports, 'stringify', ({ enumerable: true, get() {
          return codegen_1.stringify;
        } }));
        Object.defineProperty(exports, 'nil', ({ enumerable: true, get() {
          return codegen_1.nil;
        } }));
        Object.defineProperty(exports, 'Name', ({ enumerable: true, get() {
          return codegen_1.Name;
        } }));
        Object.defineProperty(exports, 'CodeGen', ({ enumerable: true, get() {
          return codegen_1.CodeGen;
        } }));
        const validation_error_1 = __webpack_require__(7426);
        Object.defineProperty(exports, 'ValidationError', ({ enumerable: true, get() {
          return validation_error_1.default;
        } }));
        const ref_error_1 = __webpack_require__(6646);
        Object.defineProperty(exports, 'MissingRefError', ({ enumerable: true, get() {
          return ref_error_1.default;
        } }));
        // # sourceMappingURL=ajv.js.map
        /***/ }),

      /***/ 7023:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.regexpCode = exports.getEsmExportName = exports.getProperty = exports.safeStringify = exports.stringify = exports.strConcat = exports.addCodeArg = exports.str = exports._ = exports.nil = exports._Code = exports.Name = exports.IDENTIFIER = exports._CodeOrName = void 0;
        class _CodeOrName {
        }
        exports._CodeOrName = _CodeOrName;
        exports.IDENTIFIER = /^[a-z$_][a-z$_0-9]*$/i;
        class Name extends _CodeOrName {
          constructor(s) {
            super();
            if (!exports.IDENTIFIER.test(s)) throw new Error('CodeGen: name must be a valid identifier');
            this.str = s;
          }
          toString() {
            return this.str;
          }
          emptyStr() {
            return false;
          }
          get names() {
            return { [this.str]: 1 };
          }
        }
        exports.Name = Name;
        class _Code extends _CodeOrName {
          constructor(code) {
            super();
            this._items = typeof code === 'string' ? [code] : code;
          }
          toString() {
            return this.str;
          }
          emptyStr() {
            if (this._items.length > 1) return false;
            const item = this._items[0];
            return item === '' || item === '""';
          }
          get str() {
            let _a;
            return ((_a = this._str) !== null && _a !== void 0 ? _a : (this._str = this._items.reduce((s, c) => `${s}${c}`, '')));
          }
          get names() {
            let _a;
            return ((_a = this._names) !== null && _a !== void 0 ? _a : (this._names = this._items.reduce((names, c) => {
              if (c instanceof Name) names[c.str] = (names[c.str] || 0) + 1;
              return names;
            }, {})));
          }
        }
        exports._Code = _Code;
        exports.nil = new _Code('');
        function _(strs, ...args) {
          const code = [strs[0]];
          let i = 0;
          while (i < args.length) {
            addCodeArg(code, args[i]);
            code.push(strs[++i]);
          }
          return new _Code(code);
        }
        exports._ = _;
        const plus = new _Code('+');
        function str(strs, ...args) {
          const expr = [safeStringify(strs[0])];
          let i = 0;
          while (i < args.length) {
            expr.push(plus);
            addCodeArg(expr, args[i]);
            expr.push(plus, safeStringify(strs[++i]));
          }
          optimize(expr);
          return new _Code(expr);
        }
        exports.str = str;
        function addCodeArg(code, arg) {
          if (arg instanceof _Code) code.push(...arg._items);
          else if (arg instanceof Name) code.push(arg);
          else code.push(interpolate(arg));
        }
        exports.addCodeArg = addCodeArg;
        function optimize(expr) {
          let i = 1;
          while (i < expr.length - 1) {
            if (expr[i] === plus) {
              const res = mergeExprItems(expr[i - 1], expr[i + 1]);
              if (res !== undefined) {
                expr.splice(i - 1, 3, res);
                continue;
              }
              expr[i++] = '+';
            }
            i++;
          }
        }
        function mergeExprItems(a, b) {
          if (b === '""') return a;
          if (a === '""') return b;
          if (typeof a === 'string') {
            if (b instanceof Name || a[a.length - 1] !== '"') return;
            if (typeof b !== 'string') return `${a.slice(0, -1)}${b}"`;
            if (b[0] === '"') return a.slice(0, -1) + b.slice(1);
            return;
          }
          if (typeof b === 'string' && b[0] === '"' && !(a instanceof Name)) return `"${a}${b.slice(1)}`;
          return;
        }
        function strConcat(c1, c2) {
          return c2.emptyStr() ? c1 : c1.emptyStr() ? c2 : str `${c1}${c2}`;
        }
        exports.strConcat = strConcat;
        // TODO do not allow arrays here
        function interpolate(x) {
          return typeof x === 'number' || typeof x === 'boolean' || x === null
            ? x
            : safeStringify(Array.isArray(x) ? x.join(',') : x);
        }
        function stringify(x) {
          return new _Code(safeStringify(x));
        }
        exports.stringify = stringify;
        function safeStringify(x) {
          return JSON.stringify(x)
            .replace(/\u2028/g, '\\u2028')
            .replace(/\u2029/g, '\\u2029');
        }
        exports.safeStringify = safeStringify;
        function getProperty(key) {
          return typeof key === 'string' && exports.IDENTIFIER.test(key) ? new _Code(`.${key}`) : _ `[${key}]`;
        }
        exports.getProperty = getProperty;
        // Does best effort to format the name properly
        function getEsmExportName(key) {
          if (typeof key === 'string' && exports.IDENTIFIER.test(key)) {
            return new _Code(`${key}`);
          }
          throw new Error(`CodeGen: invalid export name: ${key}, use explicit $id name mapping`);
        }
        exports.getEsmExportName = getEsmExportName;
        function regexpCode(rx) {
          return new _Code(rx.toString());
        }
        exports.regexpCode = regexpCode;
        // # sourceMappingURL=code.js.map
        /***/ }),

      /***/ 3487:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.or = exports.and = exports.not = exports.CodeGen = exports.operators = exports.varKinds = exports.ValueScopeName = exports.ValueScope = exports.Scope = exports.Name = exports.regexpCode = exports.stringify = exports.getProperty = exports.nil = exports.strConcat = exports.str = exports._ = void 0;
        const code_1 = __webpack_require__(7023);
        const scope_1 = __webpack_require__(8490);
        const code_2 = __webpack_require__(7023);
        Object.defineProperty(exports, '_', ({ enumerable: true, get() {
          return code_2._;
        } }));
        Object.defineProperty(exports, 'str', ({ enumerable: true, get() {
          return code_2.str;
        } }));
        Object.defineProperty(exports, 'strConcat', ({ enumerable: true, get() {
          return code_2.strConcat;
        } }));
        Object.defineProperty(exports, 'nil', ({ enumerable: true, get() {
          return code_2.nil;
        } }));
        Object.defineProperty(exports, 'getProperty', ({ enumerable: true, get() {
          return code_2.getProperty;
        } }));
        Object.defineProperty(exports, 'stringify', ({ enumerable: true, get() {
          return code_2.stringify;
        } }));
        Object.defineProperty(exports, 'regexpCode', ({ enumerable: true, get() {
          return code_2.regexpCode;
        } }));
        Object.defineProperty(exports, 'Name', ({ enumerable: true, get() {
          return code_2.Name;
        } }));
        const scope_2 = __webpack_require__(8490);
        Object.defineProperty(exports, 'Scope', ({ enumerable: true, get() {
          return scope_2.Scope;
        } }));
        Object.defineProperty(exports, 'ValueScope', ({ enumerable: true, get() {
          return scope_2.ValueScope;
        } }));
        Object.defineProperty(exports, 'ValueScopeName', ({ enumerable: true, get() {
          return scope_2.ValueScopeName;
        } }));
        Object.defineProperty(exports, 'varKinds', ({ enumerable: true, get() {
          return scope_2.varKinds;
        } }));
        exports.operators = {
          GT: new code_1._Code('>'),
          GTE: new code_1._Code('>='),
          LT: new code_1._Code('<'),
          LTE: new code_1._Code('<='),
          EQ: new code_1._Code('==='),
          NEQ: new code_1._Code('!=='),
          NOT: new code_1._Code('!'),
          OR: new code_1._Code('||'),
          AND: new code_1._Code('&&'),
          ADD: new code_1._Code('+'),
        };
        class Node {
          optimizeNodes() {
            return this;
          }
          optimizeNames(_names, _constants) {
            return this;
          }
        }
        class Def extends Node {
          constructor(varKind, name, rhs) {
            super();
            this.varKind = varKind;
            this.name = name;
            this.rhs = rhs;
          }
          render({ es5, _n }) {
            const varKind = es5 ? scope_1.varKinds.var : this.varKind;
            const rhs = this.rhs === undefined ? '' : ` = ${this.rhs}`;
            return `${varKind} ${this.name}${rhs};${_n}`;
          }
          optimizeNames(names, constants) {
            if (!names[this.name.str]) return;
            if (this.rhs) this.rhs = optimizeExpr(this.rhs, names, constants);
            return this;
          }
          get names() {
            return this.rhs instanceof code_1._CodeOrName ? this.rhs.names : {};
          }
        }
        class Assign extends Node {
          constructor(lhs, rhs, sideEffects) {
            super();
            this.lhs = lhs;
            this.rhs = rhs;
            this.sideEffects = sideEffects;
          }
          render({ _n }) {
            return `${this.lhs} = ${this.rhs};${_n}`;
          }
          optimizeNames(names, constants) {
            if (this.lhs instanceof code_1.Name && !names[this.lhs.str] && !this.sideEffects) return;
            this.rhs = optimizeExpr(this.rhs, names, constants);
            return this;
          }
          get names() {
            const names = this.lhs instanceof code_1.Name ? {} : { ...this.lhs.names };
            return addExprNames(names, this.rhs);
          }
        }
        class AssignOp extends Assign {
          constructor(lhs, op, rhs, sideEffects) {
            super(lhs, rhs, sideEffects);
            this.op = op;
          }
          render({ _n }) {
            return `${this.lhs} ${this.op}= ${this.rhs};${_n}`;
          }
        }
        class Label extends Node {
          constructor(label) {
            super();
            this.label = label;
            this.names = {};
          }
          render({ _n }) {
            return `${this.label}:${_n}`;
          }
        }
        class Break extends Node {
          constructor(label) {
            super();
            this.label = label;
            this.names = {};
          }
          render({ _n }) {
            const label = this.label ? ` ${this.label}` : '';
            return `break${label};${_n}`;
          }
        }
        class Throw extends Node {
          constructor(error) {
            super();
            this.error = error;
          }
          render({ _n }) {
            return `throw ${this.error};${_n}`;
          }
          get names() {
            return this.error.names;
          }
        }
        class AnyCode extends Node {
          constructor(code) {
            super();
            this.code = code;
          }
          render({ _n }) {
            return `${this.code};${_n}`;
          }
          optimizeNodes() {
            return `${this.code}` ? this : undefined;
          }
          optimizeNames(names, constants) {
            this.code = optimizeExpr(this.code, names, constants);
            return this;
          }
          get names() {
            return this.code instanceof code_1._CodeOrName ? this.code.names : {};
          }
        }
        class ParentNode extends Node {
          constructor(nodes = []) {
            super();
            this.nodes = nodes;
          }
          render(opts) {
            return this.nodes.reduce((code, n) => code + n.render(opts), '');
          }
          optimizeNodes() {
            const { nodes } = this;
            let i = nodes.length;
            while (i--) {
              const n = nodes[i].optimizeNodes();
              if (Array.isArray(n)) nodes.splice(i, 1, ...n);
              else if (n) nodes[i] = n;
              else nodes.splice(i, 1);
            }
            return nodes.length > 0 ? this : undefined;
          }
          optimizeNames(names, constants) {
            const { nodes } = this;
            let i = nodes.length;
            while (i--) {
            // iterating backwards improves 1-pass optimization
              const n = nodes[i];
              if (n.optimizeNames(names, constants)) continue;
              subtractNames(names, n.names);
              nodes.splice(i, 1);
            }
            return nodes.length > 0 ? this : undefined;
          }
          get names() {
            return this.nodes.reduce((names, n) => addNames(names, n.names), {});
          }
        }
        class BlockNode extends ParentNode {
          render(opts) {
            return `{${opts._n}${super.render(opts)}}${opts._n}`;
          }
        }
        class Root extends ParentNode {
        }
        class Else extends BlockNode {
        }
        Else.kind = 'else';
        class If extends BlockNode {
          constructor(condition, nodes) {
            super(nodes);
            this.condition = condition;
          }
          render(opts) {
            let code = `if(${this.condition})${super.render(opts)}`;
            if (this.else) code += `else ${this.else.render(opts)}`;
            return code;
          }
          optimizeNodes() {
            super.optimizeNodes();
            const cond = this.condition;
            if (cond === true) return this.nodes; // else is ignored here
            let e = this.else;
            if (e) {
              const ns = e.optimizeNodes();
              e = this.else = Array.isArray(ns) ? new Else(ns) : ns;
            }
            if (e) {
              if (cond === false) return e instanceof If ? e : e.nodes;
              if (this.nodes.length) return this;
              return new If(not(cond), e instanceof If ? [e] : e.nodes);
            }
            if (cond === false || !this.nodes.length) return undefined;
            return this;
          }
          optimizeNames(names, constants) {
            let _a;
            this.else = (_a = this.else) === null || _a === void 0 ? void 0 : _a.optimizeNames(names, constants);
            if (!(super.optimizeNames(names, constants) || this.else)) return;
            this.condition = optimizeExpr(this.condition, names, constants);
            return this;
          }
          get names() {
            const names = super.names;
            addExprNames(names, this.condition);
            if (this.else) addNames(names, this.else.names);
            return names;
          }
        }
        If.kind = 'if';
        class For extends BlockNode {
        }
        For.kind = 'for';
        class ForLoop extends For {
          constructor(iteration) {
            super();
            this.iteration = iteration;
          }
          render(opts) {
            return `for(${this.iteration})${super.render(opts)}`;
          }
          optimizeNames(names, constants) {
            if (!super.optimizeNames(names, constants)) return;
            this.iteration = optimizeExpr(this.iteration, names, constants);
            return this;
          }
          get names() {
            return addNames(super.names, this.iteration.names);
          }
        }
        class ForRange extends For {
          constructor(varKind, name, from, to) {
            super();
            this.varKind = varKind;
            this.name = name;
            this.from = from;
            this.to = to;
          }
          render(opts) {
            const varKind = opts.es5 ? scope_1.varKinds.var : this.varKind;
            const { name, from, to } = this;
            return `for(${varKind} ${name}=${from}; ${name}<${to}; ${name}++)${super.render(opts)}`;
          }
          get names() {
            const names = addExprNames(super.names, this.from);
            return addExprNames(names, this.to);
          }
        }
        class ForIter extends For {
          constructor(loop, varKind, name, iterable) {
            super();
            this.loop = loop;
            this.varKind = varKind;
            this.name = name;
            this.iterable = iterable;
          }
          render(opts) {
            return `for(${this.varKind} ${this.name} ${this.loop} ${this.iterable})${super.render(opts)}`;
          }
          optimizeNames(names, constants) {
            if (!super.optimizeNames(names, constants)) return;
            this.iterable = optimizeExpr(this.iterable, names, constants);
            return this;
          }
          get names() {
            return addNames(super.names, this.iterable.names);
          }
        }
        class Func extends BlockNode {
          constructor(name, args, async) {
            super();
            this.name = name;
            this.args = args;
            this.async = async;
          }
          render(opts) {
            const _async = this.async ? 'async ' : '';
            return `${_async}function ${this.name}(${this.args})${super.render(opts)}`;
          }
        }
        Func.kind = 'func';
        class Return extends ParentNode {
          render(opts) {
            return `return ${super.render(opts)}`;
          }
        }
        Return.kind = 'return';
        class Try extends BlockNode {
          render(opts) {
            let code = `try${super.render(opts)}`;
            if (this.catch) code += this.catch.render(opts);
            if (this.finally) code += this.finally.render(opts);
            return code;
          }
          optimizeNodes() {
            let _a; let _b;
            super.optimizeNodes();
            (_a = this.catch) === null || _a === void 0 ? void 0 : _a.optimizeNodes();
            (_b = this.finally) === null || _b === void 0 ? void 0 : _b.optimizeNodes();
            return this;
          }
          optimizeNames(names, constants) {
            let _a; let _b;
            super.optimizeNames(names, constants);
            (_a = this.catch) === null || _a === void 0 ? void 0 : _a.optimizeNames(names, constants);
            (_b = this.finally) === null || _b === void 0 ? void 0 : _b.optimizeNames(names, constants);
            return this;
          }
          get names() {
            const names = super.names;
            if (this.catch) addNames(names, this.catch.names);
            if (this.finally) addNames(names, this.finally.names);
            return names;
          }
        }
        class Catch extends BlockNode {
          constructor(error) {
            super();
            this.error = error;
          }
          render(opts) {
            return `catch(${this.error})${super.render(opts)}`;
          }
        }
        Catch.kind = 'catch';
        class Finally extends BlockNode {
          render(opts) {
            return `finally${super.render(opts)}`;
          }
        }
        Finally.kind = 'finally';
        class CodeGen {
          constructor(extScope, opts = {}) {
            this._values = {};
            this._blockStarts = [];
            this._constants = {};
            this.opts = { ...opts, _n: opts.lines ? '\n' : '' };
            this._extScope = extScope;
            this._scope = new scope_1.Scope({ parent: extScope });
            this._nodes = [new Root()];
          }
          toString() {
            return this._root.render(this.opts);
          }
          // returns unique name in the internal scope
          name(prefix) {
            return this._scope.name(prefix);
          }
          // reserves unique name in the external scope
          scopeName(prefix) {
            return this._extScope.name(prefix);
          }
          // reserves unique name in the external scope and assigns value to it
          scopeValue(prefixOrName, value) {
            const name = this._extScope.value(prefixOrName, value);
            const vs = this._values[name.prefix] || (this._values[name.prefix] = new Set());
            vs.add(name);
            return name;
          }
          getScopeValue(prefix, keyOrRef) {
            return this._extScope.getValue(prefix, keyOrRef);
          }
          // return code that assigns values in the external scope to the names that are used internally
          // (same names that were returned by gen.scopeName or gen.scopeValue)
          scopeRefs(scopeName) {
            return this._extScope.scopeRefs(scopeName, this._values);
          }
          scopeCode() {
            return this._extScope.scopeCode(this._values);
          }
          _def(varKind, nameOrPrefix, rhs, constant) {
            const name = this._scope.toName(nameOrPrefix);
            if (rhs !== undefined && constant) this._constants[name.str] = rhs;
            this._leafNode(new Def(varKind, name, rhs));
            return name;
          }
          // `const` declaration (`var` in es5 mode)
          const(nameOrPrefix, rhs, _constant) {
            return this._def(scope_1.varKinds.const, nameOrPrefix, rhs, _constant);
          }
          // `let` declaration with optional assignment (`var` in es5 mode)
          let(nameOrPrefix, rhs, _constant) {
            return this._def(scope_1.varKinds.let, nameOrPrefix, rhs, _constant);
          }
          // `var` declaration with optional assignment
          var(nameOrPrefix, rhs, _constant) {
            return this._def(scope_1.varKinds.var, nameOrPrefix, rhs, _constant);
          }
          // assignment code
          assign(lhs, rhs, sideEffects) {
            return this._leafNode(new Assign(lhs, rhs, sideEffects));
          }
          // `+=` code
          add(lhs, rhs) {
            return this._leafNode(new AssignOp(lhs, exports.operators.ADD, rhs));
          }
          // appends passed SafeExpr to code or executes Block
          code(c) {
            if (typeof c === 'function') c();
            else if (c !== code_1.nil) this._leafNode(new AnyCode(c));
            return this;
          }
          // returns code for object literal for the passed argument list of key-value pairs
          object(...keyValues) {
            const code = ['{'];
            for (const [key, value] of keyValues) {
              if (code.length > 1) code.push(',');
              code.push(key);
              if (key !== value || this.opts.es5) {
                code.push(':');
                (0, code_1.addCodeArg)(code, value);
              }
            }
            code.push('}');
            return new code_1._Code(code);
          }
          // `if` clause (or statement if `thenBody` and, optionally, `elseBody` are passed)
          if(condition, thenBody, elseBody) {
            this._blockNode(new If(condition));
            if (thenBody && elseBody) {
              this.code(thenBody).else()
                .code(elseBody)
                .endIf();
            } else if (thenBody) {
              this.code(thenBody).endIf();
            } else if (elseBody) {
              throw new Error('CodeGen: "else" body without "then" body');
            }
            return this;
          }
          // `else if` clause - invalid without `if` or after `else` clauses
          elseIf(condition) {
            return this._elseNode(new If(condition));
          }
          // `else` clause - only valid after `if` or `else if` clauses
          else() {
            return this._elseNode(new Else());
          }
          // end `if` statement (needed if gen.if was used only with condition)
          endIf() {
            return this._endBlockNode(If, Else);
          }
          _for(node, forBody) {
            this._blockNode(node);
            if (forBody) this.code(forBody).endFor();
            return this;
          }
          // a generic `for` clause (or statement if `forBody` is passed)
          for(iteration, forBody) {
            return this._for(new ForLoop(iteration), forBody);
          }
          // `for` statement for a range of values
          forRange(nameOrPrefix, from, to, forBody, varKind = this.opts.es5 ? scope_1.varKinds.var : scope_1.varKinds.let) {
            const name = this._scope.toName(nameOrPrefix);
            return this._for(new ForRange(varKind, name, from, to), () => forBody(name));
          }
          // `for-of` statement (in es5 mode replace with a normal for loop)
          forOf(nameOrPrefix, iterable, forBody, varKind = scope_1.varKinds.const) {
            const name = this._scope.toName(nameOrPrefix);
            if (this.opts.es5) {
              const arr = iterable instanceof code_1.Name ? iterable : this.var('_arr', iterable);
              return this.forRange('_i', 0, (0, code_1._) `${arr}.length`, (i) => {
                this.var(name, (0, code_1._) `${arr}[${i}]`);
                forBody(name);
              });
            }
            return this._for(new ForIter('of', varKind, name, iterable), () => forBody(name));
          }
          // `for-in` statement.
          // With option `ownProperties` replaced with a `for-of` loop for object keys
          forIn(nameOrPrefix, obj, forBody, varKind = this.opts.es5 ? scope_1.varKinds.var : scope_1.varKinds.const) {
            if (this.opts.ownProperties) {
              return this.forOf(nameOrPrefix, (0, code_1._) `Object.keys(${obj})`, forBody);
            }
            const name = this._scope.toName(nameOrPrefix);
            return this._for(new ForIter('in', varKind, name, obj), () => forBody(name));
          }
          // end `for` loop
          endFor() {
            return this._endBlockNode(For);
          }
          // `label` statement
          label(label) {
            return this._leafNode(new Label(label));
          }
          // `break` statement
          break(label) {
            return this._leafNode(new Break(label));
          }
          // `return` statement
          return(value) {
            const node = new Return();
            this._blockNode(node);
            this.code(value);
            if (node.nodes.length !== 1) throw new Error('CodeGen: "return" should have one node');
            return this._endBlockNode(Return);
          }
          // `try` statement
          try(tryBody, catchCode, finallyCode) {
            if (!catchCode && !finallyCode) throw new Error('CodeGen: "try" without "catch" and "finally"');
            const node = new Try();
            this._blockNode(node);
            this.code(tryBody);
            if (catchCode) {
              const error = this.name('e');
              this._currNode = node.catch = new Catch(error);
              catchCode(error);
            }
            if (finallyCode) {
              this._currNode = node.finally = new Finally();
              this.code(finallyCode);
            }
            return this._endBlockNode(Catch, Finally);
          }
          // `throw` statement
          throw(error) {
            return this._leafNode(new Throw(error));
          }
          // start self-balancing block
          block(body, nodeCount) {
            this._blockStarts.push(this._nodes.length);
            if (body) this.code(body).endBlock(nodeCount);
            return this;
          }
          // end the current self-balancing block
          endBlock(nodeCount) {
            const len = this._blockStarts.pop();
            if (len === undefined) throw new Error('CodeGen: not in self-balancing block');
            const toClose = this._nodes.length - len;
            if (toClose < 0 || (nodeCount !== undefined && toClose !== nodeCount)) {
              throw new Error(`CodeGen: wrong number of nodes: ${toClose} vs ${nodeCount} expected`);
            }
            this._nodes.length = len;
            return this;
          }
          // `function` heading (or definition if funcBody is passed)
          func(name, args = code_1.nil, async, funcBody) {
            this._blockNode(new Func(name, args, async));
            if (funcBody) this.code(funcBody).endFunc();
            return this;
          }
          // end function definition
          endFunc() {
            return this._endBlockNode(Func);
          }
          optimize(n = 1) {
            while (n-- > 0) {
              this._root.optimizeNodes();
              this._root.optimizeNames(this._root.names, this._constants);
            }
          }
          _leafNode(node) {
            this._currNode.nodes.push(node);
            return this;
          }
          _blockNode(node) {
            this._currNode.nodes.push(node);
            this._nodes.push(node);
          }
          _endBlockNode(N1, N2) {
            const n = this._currNode;
            if (n instanceof N1 || (N2 && n instanceof N2)) {
              this._nodes.pop();
              return this;
            }
            throw new Error(`CodeGen: not in block "${N2 ? `${N1.kind}/${N2.kind}` : N1.kind}"`);
          }
          _elseNode(node) {
            const n = this._currNode;
            if (!(n instanceof If)) {
              throw new Error('CodeGen: "else" without "if"');
            }
            this._currNode = n.else = node;
            return this;
          }
          get _root() {
            return this._nodes[0];
          }
          get _currNode() {
            const ns = this._nodes;
            return ns[ns.length - 1];
          }
          set _currNode(node) {
            const ns = this._nodes;
            ns[ns.length - 1] = node;
          }
        }
        exports.CodeGen = CodeGen;
        function addNames(names, from) {
          for (const n in from) names[n] = (names[n] || 0) + (from[n] || 0);
          return names;
        }
        function addExprNames(names, from) {
          return from instanceof code_1._CodeOrName ? addNames(names, from.names) : names;
        }
        function optimizeExpr(expr, names, constants) {
          if (expr instanceof code_1.Name) return replaceName(expr);
          if (!canOptimize(expr)) return expr;
          return new code_1._Code(expr._items.reduce((items, c) => {
            if (c instanceof code_1.Name) c = replaceName(c);
            if (c instanceof code_1._Code) items.push(...c._items);
            else items.push(c);
            return items;
          }, []));
          function replaceName(n) {
            const c = constants[n.str];
            if (c === undefined || names[n.str] !== 1) return n;
            delete names[n.str];
            return c;
          }
          function canOptimize(e) {
            return (e instanceof code_1._Code
            && e._items.some(c => c instanceof code_1.Name && names[c.str] === 1 && constants[c.str] !== undefined));
          }
        }
        function subtractNames(names, from) {
          for (const n in from) names[n] = (names[n] || 0) - (from[n] || 0);
        }
        function not(x) {
          return typeof x === 'boolean' || typeof x === 'number' || x === null ? !x : (0, code_1._) `!${par(x)}`;
        }
        exports.not = not;
        const andCode = mappend(exports.operators.AND);
        // boolean AND (&&) expression with the passed arguments
        function and(...args) {
          return args.reduce(andCode);
        }
        exports.and = and;
        const orCode = mappend(exports.operators.OR);
        // boolean OR (||) expression with the passed arguments
        function or(...args) {
          return args.reduce(orCode);
        }
        exports.or = or;
        function mappend(op) {
          return (x, y) => (x === code_1.nil ? y : y === code_1.nil ? x : (0, code_1._) `${par(x)} ${op} ${par(y)}`);
        }
        function par(x) {
          return x instanceof code_1.Name ? x : (0, code_1._) `(${x})`;
        }
        // # sourceMappingURL=index.js.map
        /***/ }),

      /***/ 8490:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.ValueScope = exports.ValueScopeName = exports.Scope = exports.varKinds = exports.UsedValueState = void 0;
        const code_1 = __webpack_require__(7023);
        class ValueError extends Error {
          constructor(name) {
            super(`CodeGen: "code" for ${name} not defined`);
            this.value = name.value;
          }
        }
        let UsedValueState;
        (function (UsedValueState) {
          UsedValueState[UsedValueState.Started = 0] = 'Started';
          UsedValueState[UsedValueState.Completed = 1] = 'Completed';
        }(UsedValueState = exports.UsedValueState || (exports.UsedValueState = {})));
        exports.varKinds = {
          const: new code_1.Name('const'),
          let: new code_1.Name('let'),
          var: new code_1.Name('var'),
        };
        class Scope {
          constructor({ prefixes, parent } = {}) {
            this._names = {};
            this._prefixes = prefixes;
            this._parent = parent;
          }
          toName(nameOrPrefix) {
            return nameOrPrefix instanceof code_1.Name ? nameOrPrefix : this.name(nameOrPrefix);
          }
          name(prefix) {
            return new code_1.Name(this._newName(prefix));
          }
          _newName(prefix) {
            const ng = this._names[prefix] || this._nameGroup(prefix);
            return `${prefix}${ng.index++}`;
          }
          _nameGroup(prefix) {
            let _a; let _b;
            if (((_b = (_a = this._parent) === null || _a === void 0 ? void 0 : _a._prefixes) === null || _b === void 0 ? void 0 : _b.has(prefix)) || (this._prefixes && !this._prefixes.has(prefix))) {
              throw new Error(`CodeGen: prefix "${prefix}" is not allowed in this scope`);
            }
            return (this._names[prefix] = { prefix, index: 0 });
          }
        }
        exports.Scope = Scope;
        class ValueScopeName extends code_1.Name {
          constructor(prefix, nameStr) {
            super(nameStr);
            this.prefix = prefix;
          }
          setValue(value, { property, itemIndex }) {
            this.value = value;
            this.scopePath = (0, code_1._) `.${new code_1.Name(property)}[${itemIndex}]`;
          }
        }
        exports.ValueScopeName = ValueScopeName;
        const line = (0, code_1._) `\n`;
        class ValueScope extends Scope {
          constructor(opts) {
            super(opts);
            this._values = {};
            this._scope = opts.scope;
            this.opts = { ...opts, _n: opts.lines ? line : code_1.nil };
          }
          get() {
            return this._scope;
          }
          name(prefix) {
            return new ValueScopeName(prefix, this._newName(prefix));
          }
          value(nameOrPrefix, value) {
            let _a;
            if (value.ref === undefined) throw new Error('CodeGen: ref must be passed in value');
            const name = this.toName(nameOrPrefix);
            const { prefix } = name;
            const valueKey = (_a = value.key) !== null && _a !== void 0 ? _a : value.ref;
            let vs = this._values[prefix];
            if (vs) {
              const _name = vs.get(valueKey);
              if (_name) return _name;
            } else {
              vs = this._values[prefix] = new Map();
            }
            vs.set(valueKey, name);
            const s = this._scope[prefix] || (this._scope[prefix] = []);
            const itemIndex = s.length;
            s[itemIndex] = value.ref;
            name.setValue(value, { property: prefix, itemIndex });
            return name;
          }
          getValue(prefix, keyOrRef) {
            const vs = this._values[prefix];
            if (!vs) return;
            return vs.get(keyOrRef);
          }
          scopeRefs(scopeName, values = this._values) {
            return this._reduceValues(values, (name) => {
              if (name.scopePath === undefined) throw new Error(`CodeGen: name "${name}" has no value`);
              return (0, code_1._) `${scopeName}${name.scopePath}`;
            });
          }
          scopeCode(values = this._values, usedValues, getCode) {
            return this._reduceValues(values, (name) => {
              if (name.value === undefined) throw new Error(`CodeGen: name "${name}" has no value`);
              return name.value.code;
            }, usedValues, getCode);
          }
          _reduceValues(values, valueCode, usedValues = {}, getCode) {
            let code = code_1.nil;
            for (const prefix in values) {
              const vs = values[prefix];
              if (!vs) continue;
              const nameSet = (usedValues[prefix] = usedValues[prefix] || new Map());
              vs.forEach((name) => {
                if (nameSet.has(name)) return;
                nameSet.set(name, UsedValueState.Started);
                let c = valueCode(name);
                if (c) {
                  const def = this.opts.es5 ? exports.varKinds.var : exports.varKinds.const;
                  code = (0, code_1._) `${code}${def} ${name} = ${c};${this.opts._n}`;
                } else if ((c = getCode === null || getCode === void 0 ? void 0 : getCode(name))) {
                  code = (0, code_1._) `${code}${c}${this.opts._n}`;
                } else {
                  throw new ValueError(name);
                }
                nameSet.set(name, UsedValueState.Completed);
              });
            }
            return code;
          }
        }
        exports.ValueScope = ValueScope;
        // # sourceMappingURL=scope.js.map
        /***/ }),

      /***/ 4181:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.extendErrors = exports.resetErrorsCount = exports.reportExtraError = exports.reportError = exports.keyword$DataError = exports.keywordError = void 0;
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const names_1 = __webpack_require__(2141);
        exports.keywordError = {
          message: ({ keyword }) => (0, codegen_1.str) `must pass "${keyword}" keyword validation`,
        };
        exports.keyword$DataError = {
          message: ({ keyword, schemaType }) => (schemaType
            ? (0, codegen_1.str) `"${keyword}" keyword must be ${schemaType} ($data)`
            : (0, codegen_1.str) `"${keyword}" keyword is invalid ($data)`),
        };
        function reportError(cxt, error = exports.keywordError, errorPaths, overrideAllErrors) {
          const { it } = cxt;
          const { gen, compositeRule, allErrors } = it;
          const errObj = errorObjectCode(cxt, error, errorPaths);
          if (overrideAllErrors !== null && overrideAllErrors !== void 0 ? overrideAllErrors : (compositeRule || allErrors)) {
            addError(gen, errObj);
          } else {
            returnErrors(it, (0, codegen_1._) `[${errObj}]`);
          }
        }
        exports.reportError = reportError;
        function reportExtraError(cxt, error = exports.keywordError, errorPaths) {
          const { it } = cxt;
          const { gen, compositeRule, allErrors } = it;
          const errObj = errorObjectCode(cxt, error, errorPaths);
          addError(gen, errObj);
          if (!(compositeRule || allErrors)) {
            returnErrors(it, names_1.default.vErrors);
          }
        }
        exports.reportExtraError = reportExtraError;
        function resetErrorsCount(gen, errsCount) {
          gen.assign(names_1.default.errors, errsCount);
          gen.if((0, codegen_1._) `${names_1.default.vErrors} !== null`, () => gen.if(errsCount, () => gen.assign((0, codegen_1._) `${names_1.default.vErrors}.length`, errsCount), () => gen.assign(names_1.default.vErrors, null)));
        }
        exports.resetErrorsCount = resetErrorsCount;
        function extendErrors({ gen, keyword, schemaValue, data, errsCount, it }) {
          /* istanbul ignore if */
          if (errsCount === undefined) throw new Error('ajv implementation error');
          const err = gen.name('err');
          gen.forRange('i', errsCount, names_1.default.errors, (i) => {
            gen.const(err, (0, codegen_1._) `${names_1.default.vErrors}[${i}]`);
            gen.if((0, codegen_1._) `${err}.instancePath === undefined`, () => gen.assign((0, codegen_1._) `${err}.instancePath`, (0, codegen_1.strConcat)(names_1.default.instancePath, it.errorPath)));
            gen.assign((0, codegen_1._) `${err}.schemaPath`, (0, codegen_1.str) `${it.errSchemaPath}/${keyword}`);
            if (it.opts.verbose) {
              gen.assign((0, codegen_1._) `${err}.schema`, schemaValue);
              gen.assign((0, codegen_1._) `${err}.data`, data);
            }
          });
        }
        exports.extendErrors = extendErrors;
        function addError(gen, errObj) {
          const err = gen.const('err', errObj);
          gen.if((0, codegen_1._) `${names_1.default.vErrors} === null`, () => gen.assign(names_1.default.vErrors, (0, codegen_1._) `[${err}]`), (0, codegen_1._) `${names_1.default.vErrors}.push(${err})`);
          gen.code((0, codegen_1._) `${names_1.default.errors}++`);
        }
        function returnErrors(it, errs) {
          const { gen, validateName, schemaEnv } = it;
          if (schemaEnv.$async) {
            gen.throw((0, codegen_1._) `new ${it.ValidationError}(${errs})`);
          } else {
            gen.assign((0, codegen_1._) `${validateName}.errors`, errs);
            gen.return(false);
          }
        }
        const E = {
          keyword: new codegen_1.Name('keyword'),
          schemaPath: new codegen_1.Name('schemaPath'),
          params: new codegen_1.Name('params'),
          propertyName: new codegen_1.Name('propertyName'),
          message: new codegen_1.Name('message'),
          schema: new codegen_1.Name('schema'),
          parentSchema: new codegen_1.Name('parentSchema'),
        };
        function errorObjectCode(cxt, error, errorPaths) {
          const { createErrors } = cxt.it;
          if (createErrors === false) return (0, codegen_1._) `{}`;
          return errorObject(cxt, error, errorPaths);
        }
        function errorObject(cxt, error, errorPaths = {}) {
          const { gen, it } = cxt;
          const keyValues = [
            errorInstancePath(it, errorPaths),
            errorSchemaPath(cxt, errorPaths),
          ];
          extraErrorProps(cxt, error, keyValues);
          return gen.object(...keyValues);
        }
        function errorInstancePath({ errorPath }, { instancePath }) {
          const instPath = instancePath
            ? (0, codegen_1.str) `${errorPath}${(0, util_1.getErrorPath)(instancePath, util_1.Type.Str)}`
            : errorPath;
          return [names_1.default.instancePath, (0, codegen_1.strConcat)(names_1.default.instancePath, instPath)];
        }
        function errorSchemaPath({ keyword, it: { errSchemaPath } }, { schemaPath, parentSchema }) {
          let schPath = parentSchema ? errSchemaPath : (0, codegen_1.str) `${errSchemaPath}/${keyword}`;
          if (schemaPath) {
            schPath = (0, codegen_1.str) `${schPath}${(0, util_1.getErrorPath)(schemaPath, util_1.Type.Str)}`;
          }
          return [E.schemaPath, schPath];
        }
        function extraErrorProps(cxt, { params, message }, keyValues) {
          const { keyword, data, schemaValue, it } = cxt;
          const { opts, propertyName, topSchemaRef, schemaPath } = it;
          keyValues.push([E.keyword, keyword], [E.params, typeof params === 'function' ? params(cxt) : params || (0, codegen_1._) `{}`]);
          if (opts.messages) {
            keyValues.push([E.message, typeof message === 'function' ? message(cxt) : message]);
          }
          if (opts.verbose) {
            keyValues.push([E.schema, schemaValue], [E.parentSchema, (0, codegen_1._) `${topSchemaRef}${schemaPath}`], [names_1.default.data, data]);
          }
          if (propertyName) keyValues.push([E.propertyName, propertyName]);
        }
        // # sourceMappingURL=errors.js.map
        /***/ }),

      /***/ 5173:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.resolveSchema = exports.getCompilingSchema = exports.resolveRef = exports.compileSchema = exports.SchemaEnv = void 0;
        const codegen_1 = __webpack_require__(3487);
        const validation_error_1 = __webpack_require__(7426);
        const names_1 = __webpack_require__(2141);
        const resolve_1 = __webpack_require__(2531);
        const util_1 = __webpack_require__(6776);
        const validate_1 = __webpack_require__(4815);
        class SchemaEnv {
          constructor(env) {
            let _a;
            this.refs = {};
            this.dynamicAnchors = {};
            let schema;
            if (typeof env.schema === 'object') schema = env.schema;
            this.schema = env.schema;
            this.schemaId = env.schemaId;
            this.root = env.root || this;
            this.baseId = (_a = env.baseId) !== null && _a !== void 0 ? _a : (0, resolve_1.normalizeId)(schema === null || schema === void 0 ? void 0 : schema[env.schemaId || '$id']);
            this.schemaPath = env.schemaPath;
            this.localRefs = env.localRefs;
            this.meta = env.meta;
            this.$async = schema === null || schema === void 0 ? void 0 : schema.$async;
            this.refs = {};
          }
        }
        exports.SchemaEnv = SchemaEnv;
        // let codeSize = 0
        // let nodeCount = 0
        // Compiles schema in SchemaEnv
        function compileSchema(sch) {
          // TODO refactor - remove compilations
          const _sch = getCompilingSchema.call(this, sch);
          if (_sch) return _sch;
          const rootId = (0, resolve_1.getFullPath)(this.opts.uriResolver, sch.root.baseId); // TODO if getFullPath removed 1 tests fails
          const { es5, lines } = this.opts.code;
          const { ownProperties } = this.opts;
          const gen = new codegen_1.CodeGen(this.scope, { es5, lines, ownProperties });
          let _ValidationError;
          if (sch.$async) {
            _ValidationError = gen.scopeValue('Error', {
              ref: validation_error_1.default,
              code: (0, codegen_1._) `require("ajv/dist/runtime/validation_error").default`,
            });
          }
          const validateName = gen.scopeName('validate');
          sch.validateName = validateName;
          const schemaCxt = {
            gen,
            allErrors: this.opts.allErrors,
            data: names_1.default.data,
            parentData: names_1.default.parentData,
            parentDataProperty: names_1.default.parentDataProperty,
            dataNames: [names_1.default.data],
            dataPathArr: [codegen_1.nil],
            dataLevel: 0,
            dataTypes: [],
            definedProperties: new Set(),
            topSchemaRef: gen.scopeValue('schema', this.opts.code.source === true
              ? { ref: sch.schema, code: (0, codegen_1.stringify)(sch.schema) }
              : { ref: sch.schema }),
            validateName,
            ValidationError: _ValidationError,
            schema: sch.schema,
            schemaEnv: sch,
            rootId,
            baseId: sch.baseId || rootId,
            schemaPath: codegen_1.nil,
            errSchemaPath: sch.schemaPath || (this.opts.jtd ? '' : '#'),
            errorPath: (0, codegen_1._) `""`,
            opts: this.opts,
            self: this,
          };
          let sourceCode;
          try {
            this._compilations.add(sch);
            (0, validate_1.validateFunctionCode)(schemaCxt);
            gen.optimize(this.opts.code.optimize);
            // gen.optimize(1)
            const validateCode = gen.toString();
            sourceCode = `${gen.scopeRefs(names_1.default.scope)}return ${validateCode}`;
            // console.log((codeSize += sourceCode.length), (nodeCount += gen.nodeCount))
            if (this.opts.code.process) sourceCode = this.opts.code.process(sourceCode, sch);
            // console.log("\n\n\n *** \n", sourceCode)
            const makeValidate = new Function(`${names_1.default.self}`, `${names_1.default.scope}`, sourceCode);
            const validate = makeValidate(this, this.scope.get());
            this.scope.value(validateName, { ref: validate });
            validate.errors = null;
            validate.schema = sch.schema;
            validate.schemaEnv = sch;
            if (sch.$async) validate.$async = true;
            if (this.opts.code.source === true) {
              validate.source = { validateName, validateCode, scopeValues: gen._values };
            }
            if (this.opts.unevaluated) {
              const { props, items } = schemaCxt;
              validate.evaluated = {
                props: props instanceof codegen_1.Name ? undefined : props,
                items: items instanceof codegen_1.Name ? undefined : items,
                dynamicProps: props instanceof codegen_1.Name,
                dynamicItems: items instanceof codegen_1.Name,
              };
              if (validate.source) validate.source.evaluated = (0, codegen_1.stringify)(validate.evaluated);
            }
            sch.validate = validate;
            return sch;
          } catch (e) {
            delete sch.validate;
            delete sch.validateName;
            if (sourceCode) this.logger.error('Error compiling schema, function code:', sourceCode);
            // console.log("\n\n\n *** \n", sourceCode, this.opts)
            throw e;
          } finally {
            this._compilations.delete(sch);
          }
        }
        exports.compileSchema = compileSchema;
        function resolveRef(root, baseId, ref) {
          let _a;
          ref = (0, resolve_1.resolveUrl)(this.opts.uriResolver, baseId, ref);
          const schOrFunc = root.refs[ref];
          if (schOrFunc) return schOrFunc;
          let _sch = resolve.call(this, root, ref);
          if (_sch === undefined) {
            const schema = (_a = root.localRefs) === null || _a === void 0 ? void 0 : _a[ref]; // TODO maybe localRefs should hold SchemaEnv
            const { schemaId } = this.opts;
            if (schema) _sch = new SchemaEnv({ schema, schemaId, root, baseId });
          }
          if (_sch === undefined) return;
          return (root.refs[ref] = inlineOrCompile.call(this, _sch));
        }
        exports.resolveRef = resolveRef;
        function inlineOrCompile(sch) {
          if ((0, resolve_1.inlineRef)(sch.schema, this.opts.inlineRefs)) return sch.schema;
          return sch.validate ? sch : compileSchema.call(this, sch);
        }
        // Index of schema compilation in the currently compiled list
        function getCompilingSchema(schEnv) {
          for (const sch of this._compilations) {
            if (sameSchemaEnv(sch, schEnv)) return sch;
          }
        }
        exports.getCompilingSchema = getCompilingSchema;
        function sameSchemaEnv(s1, s2) {
          return s1.schema === s2.schema && s1.root === s2.root && s1.baseId === s2.baseId;
        }
        // resolve and compile the references ($ref)
        // TODO returns AnySchemaObject (if the schema can be inlined) or validation function
        function resolve(
          root, // information about the root schema for the current schema
          ref, // reference to resolve
        ) {
          let sch;
          while (typeof (sch = this.refs[ref]) === 'string') ref = sch;
          return sch || this.schemas[ref] || resolveSchema.call(this, root, ref);
        }
        // Resolve schema, its root and baseId
        function resolveSchema(
          root, // root object with properties schema, refs TODO below SchemaEnv is assigned to it
          ref, // reference to resolve
        ) {
          const p = this.opts.uriResolver.parse(ref);
          const refPath = (0, resolve_1._getFullPath)(this.opts.uriResolver, p);
          let baseId = (0, resolve_1.getFullPath)(this.opts.uriResolver, root.baseId, undefined);
          // TODO `Object.keys(root.schema).length > 0` should not be needed - but removing breaks 2 tests
          if (Object.keys(root.schema).length > 0 && refPath === baseId) {
            return getJsonPointer.call(this, p, root);
          }
          const id = (0, resolve_1.normalizeId)(refPath);
          const schOrRef = this.refs[id] || this.schemas[id];
          if (typeof schOrRef === 'string') {
            const sch = resolveSchema.call(this, root, schOrRef);
            if (typeof (sch === null || sch === void 0 ? void 0 : sch.schema) !== 'object') return;
            return getJsonPointer.call(this, p, sch);
          }
          if (typeof (schOrRef === null || schOrRef === void 0 ? void 0 : schOrRef.schema) !== 'object') return;
          if (!schOrRef.validate) compileSchema.call(this, schOrRef);
          if (id === (0, resolve_1.normalizeId)(ref)) {
            const { schema } = schOrRef;
            const { schemaId } = this.opts;
            const schId = schema[schemaId];
            if (schId) baseId = (0, resolve_1.resolveUrl)(this.opts.uriResolver, baseId, schId);
            return new SchemaEnv({ schema, schemaId, root, baseId });
          }
          return getJsonPointer.call(this, p, schOrRef);
        }
        exports.resolveSchema = resolveSchema;
        const PREVENT_SCOPE_CHANGE = new Set([
          'properties',
          'patternProperties',
          'enum',
          'dependencies',
          'definitions',
        ]);
        function getJsonPointer(parsedRef, { baseId, schema, root }) {
          let _a;
          if (((_a = parsedRef.fragment) === null || _a === void 0 ? void 0 : _a[0]) !== '/') return;
          for (const part of parsedRef.fragment.slice(1).split('/')) {
            if (typeof schema === 'boolean') return;
            const partSchema = schema[(0, util_1.unescapeFragment)(part)];
            if (partSchema === undefined) return;
            schema = partSchema;
            // TODO PREVENT_SCOPE_CHANGE could be defined in keyword def?
            const schId = typeof schema === 'object' && schema[this.opts.schemaId];
            if (!PREVENT_SCOPE_CHANGE.has(part) && schId) {
              baseId = (0, resolve_1.resolveUrl)(this.opts.uriResolver, baseId, schId);
            }
          }
          let env;
          if (typeof schema !== 'boolean' && schema.$ref && !(0, util_1.schemaHasRulesButRef)(schema, this.RULES)) {
            const $ref = (0, resolve_1.resolveUrl)(this.opts.uriResolver, baseId, schema.$ref);
            env = resolveSchema.call(this, root, $ref);
          }
          // even though resolution failed we need to return SchemaEnv to throw exception
          // so that compileAsync loads missing schema.
          const { schemaId } = this.opts;
          env = env || new SchemaEnv({ schema, schemaId, root, baseId });
          if (env.schema !== env.root.schema) return env;
          return undefined;
        }
        // # sourceMappingURL=index.js.map
        /***/ }),

      /***/ 2141:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const names = {
          // validation function arguments
          data: new codegen_1.Name('data'),
          // args passed from referencing schema
          valCxt: new codegen_1.Name('valCxt'),
          instancePath: new codegen_1.Name('instancePath'),
          parentData: new codegen_1.Name('parentData'),
          parentDataProperty: new codegen_1.Name('parentDataProperty'),
          rootData: new codegen_1.Name('rootData'),
          dynamicAnchors: new codegen_1.Name('dynamicAnchors'),
          // function scoped variables
          vErrors: new codegen_1.Name('vErrors'),
          errors: new codegen_1.Name('errors'),
          this: new codegen_1.Name('this'),
          // "globals"
          self: new codegen_1.Name('self'),
          scope: new codegen_1.Name('scope'),
          // JTD serialize/parse name for JSON string and position
          json: new codegen_1.Name('json'),
          jsonPos: new codegen_1.Name('jsonPos'),
          jsonLen: new codegen_1.Name('jsonLen'),
          jsonPart: new codegen_1.Name('jsonPart'),
        };
        exports.default = names;
        // # sourceMappingURL=names.js.map
        /***/ }),

      /***/ 6646:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const resolve_1 = __webpack_require__(2531);
        class MissingRefError extends Error {
          constructor(resolver, baseId, ref, msg) {
            super(msg || `can't resolve reference ${ref} from id ${baseId}`);
            this.missingRef = (0, resolve_1.resolveUrl)(resolver, baseId, ref);
            this.missingSchema = (0, resolve_1.normalizeId)((0, resolve_1.getFullPath)(resolver, this.missingRef));
          }
        }
        exports.default = MissingRefError;
        // # sourceMappingURL=ref_error.js.map
        /***/ }),

      /***/ 2531:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.getSchemaRefs = exports.resolveUrl = exports.normalizeId = exports._getFullPath = exports.getFullPath = exports.inlineRef = void 0;
        const util_1 = __webpack_require__(6776);
        const equal = __webpack_require__(4063);
        const traverse = __webpack_require__(9461);
        // TODO refactor to use keyword definitions
        const SIMPLE_INLINED = new Set([
          'type',
          'format',
          'pattern',
          'maxLength',
          'minLength',
          'maxProperties',
          'minProperties',
          'maxItems',
          'minItems',
          'maximum',
          'minimum',
          'uniqueItems',
          'multipleOf',
          'required',
          'enum',
          'const',
        ]);
        function inlineRef(schema, limit = true) {
          if (typeof schema === 'boolean') return true;
          if (limit === true) return !hasRef(schema);
          if (!limit) return false;
          return countKeys(schema) <= limit;
        }
        exports.inlineRef = inlineRef;
        const REF_KEYWORDS = new Set([
          '$ref',
          '$recursiveRef',
          '$recursiveAnchor',
          '$dynamicRef',
          '$dynamicAnchor',
        ]);
        function hasRef(schema) {
          for (const key in schema) {
            if (REF_KEYWORDS.has(key)) return true;
            const sch = schema[key];
            if (Array.isArray(sch) && sch.some(hasRef)) return true;
            if (typeof sch === 'object' && hasRef(sch)) return true;
          }
          return false;
        }
        function countKeys(schema) {
          let count = 0;
          for (const key in schema) {
            if (key === '$ref') return Infinity;
            count++;
            if (SIMPLE_INLINED.has(key)) continue;
            if (typeof schema[key] === 'object') {
              (0, util_1.eachItem)(schema[key], sch => (count += countKeys(sch)));
            }
            if (count === Infinity) return Infinity;
          }
          return count;
        }
        function getFullPath(resolver, id = '', normalize) {
          if (normalize !== false) id = normalizeId(id);
          const p = resolver.parse(id);
          return _getFullPath(resolver, p);
        }
        exports.getFullPath = getFullPath;
        function _getFullPath(resolver, p) {
          const serialized = resolver.serialize(p);
          return `${serialized.split('#')[0]}#`;
        }
        exports._getFullPath = _getFullPath;
        const TRAILING_SLASH_HASH = /#\/?$/;
        function normalizeId(id) {
          return id ? id.replace(TRAILING_SLASH_HASH, '') : '';
        }
        exports.normalizeId = normalizeId;
        function resolveUrl(resolver, baseId, id) {
          id = normalizeId(id);
          return resolver.resolve(baseId, id);
        }
        exports.resolveUrl = resolveUrl;
        const ANCHOR = /^[a-z_][-a-z0-9._]*$/i;
        function getSchemaRefs(schema, baseId) {
          if (typeof schema === 'boolean') return {};
          const { schemaId, uriResolver } = this.opts;
          const schId = normalizeId(schema[schemaId] || baseId);
          const baseIds = { '': schId };
          const pathPrefix = getFullPath(uriResolver, schId, false);
          const localRefs = {};
          const schemaRefs = new Set();
          traverse(schema, { allKeys: true }, (sch, jsonPtr, _, parentJsonPtr) => {
            if (parentJsonPtr === undefined) return;
            const fullPath = pathPrefix + jsonPtr;
            let baseId = baseIds[parentJsonPtr];
            if (typeof sch[schemaId] === 'string') baseId = addRef.call(this, sch[schemaId]);
            addAnchor.call(this, sch.$anchor);
            addAnchor.call(this, sch.$dynamicAnchor);
            baseIds[jsonPtr] = baseId;
            function addRef(ref) {
            // eslint-disable-next-line @typescript-eslint/unbound-method
              const _resolve = this.opts.uriResolver.resolve;
              ref = normalizeId(baseId ? _resolve(baseId, ref) : ref);
              if (schemaRefs.has(ref)) throw ambiguos(ref);
              schemaRefs.add(ref);
              let schOrRef = this.refs[ref];
              if (typeof schOrRef === 'string') schOrRef = this.refs[schOrRef];
              if (typeof schOrRef === 'object') {
                checkAmbiguosRef(sch, schOrRef.schema, ref);
              } else if (ref !== normalizeId(fullPath)) {
                if (ref[0] === '#') {
                  checkAmbiguosRef(sch, localRefs[ref], ref);
                  localRefs[ref] = sch;
                } else {
                  this.refs[ref] = fullPath;
                }
              }
              return ref;
            }
            function addAnchor(anchor) {
              if (typeof anchor === 'string') {
                if (!ANCHOR.test(anchor)) throw new Error(`invalid anchor "${anchor}"`);
                addRef.call(this, `#${anchor}`);
              }
            }
          });
          return localRefs;
          function checkAmbiguosRef(sch1, sch2, ref) {
            if (sch2 !== undefined && !equal(sch1, sch2)) throw ambiguos(ref);
          }
          function ambiguos(ref) {
            return new Error(`reference "${ref}" resolves to more than one schema`);
          }
        }
        exports.getSchemaRefs = getSchemaRefs;
        // # sourceMappingURL=resolve.js.map
        /***/ }),

      /***/ 3141:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.getRules = exports.isJSONType = void 0;
        const _jsonTypes = ['string', 'number', 'integer', 'boolean', 'null', 'object', 'array'];
        const jsonTypes = new Set(_jsonTypes);
        function isJSONType(x) {
          return typeof x === 'string' && jsonTypes.has(x);
        }
        exports.isJSONType = isJSONType;
        function getRules() {
          const groups = {
            number: { type: 'number', rules: [] },
            string: { type: 'string', rules: [] },
            array: { type: 'array', rules: [] },
            object: { type: 'object', rules: [] },
          };
          return {
            types: { ...groups, integer: true, boolean: true, null: true },
            rules: [{ rules: [] }, groups.number, groups.string, groups.array, groups.object],
            post: { rules: [] },
            all: {},
            keywords: {},
          };
        }
        exports.getRules = getRules;
        // # sourceMappingURL=rules.js.map
        /***/ }),

      /***/ 6776:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.checkStrictMode = exports.getErrorPath = exports.Type = exports.useFunc = exports.setEvaluated = exports.evaluatedPropsToName = exports.mergeEvaluated = exports.eachItem = exports.unescapeJsonPointer = exports.escapeJsonPointer = exports.escapeFragment = exports.unescapeFragment = exports.schemaRefOrVal = exports.schemaHasRulesButRef = exports.schemaHasRules = exports.checkUnknownRules = exports.alwaysValidSchema = exports.toHash = void 0;
        const codegen_1 = __webpack_require__(3487);
        const code_1 = __webpack_require__(7023);
        // TODO refactor to use Set
        function toHash(arr) {
          const hash = {};
          for (const item of arr) hash[item] = true;
          return hash;
        }
        exports.toHash = toHash;
        function alwaysValidSchema(it, schema) {
          if (typeof schema === 'boolean') return schema;
          if (Object.keys(schema).length === 0) return true;
          checkUnknownRules(it, schema);
          return !schemaHasRules(schema, it.self.RULES.all);
        }
        exports.alwaysValidSchema = alwaysValidSchema;
        function checkUnknownRules(it, schema = it.schema) {
          const { opts, self } = it;
          if (!opts.strictSchema) return;
          if (typeof schema === 'boolean') return;
          const rules = self.RULES.keywords;
          for (const key in schema) {
            if (!rules[key]) checkStrictMode(it, `unknown keyword: "${key}"`);
          }
        }
        exports.checkUnknownRules = checkUnknownRules;
        function schemaHasRules(schema, rules) {
          if (typeof schema === 'boolean') return !schema;
          for (const key in schema) if (rules[key]) return true;
          return false;
        }
        exports.schemaHasRules = schemaHasRules;
        function schemaHasRulesButRef(schema, RULES) {
          if (typeof schema === 'boolean') return !schema;
          for (const key in schema) if (key !== '$ref' && RULES.all[key]) return true;
          return false;
        }
        exports.schemaHasRulesButRef = schemaHasRulesButRef;
        function schemaRefOrVal({ topSchemaRef, schemaPath }, schema, keyword, $data) {
          if (!$data) {
            if (typeof schema === 'number' || typeof schema === 'boolean') return schema;
            if (typeof schema === 'string') return (0, codegen_1._) `${schema}`;
          }
          return (0, codegen_1._) `${topSchemaRef}${schemaPath}${(0, codegen_1.getProperty)(keyword)}`;
        }
        exports.schemaRefOrVal = schemaRefOrVal;
        function unescapeFragment(str) {
          return unescapeJsonPointer(decodeURIComponent(str));
        }
        exports.unescapeFragment = unescapeFragment;
        function escapeFragment(str) {
          return encodeURIComponent(escapeJsonPointer(str));
        }
        exports.escapeFragment = escapeFragment;
        function escapeJsonPointer(str) {
          if (typeof str === 'number') return `${str}`;
          return str.replace(/~/g, '~0').replace(/\//g, '~1');
        }
        exports.escapeJsonPointer = escapeJsonPointer;
        function unescapeJsonPointer(str) {
          return str.replace(/~1/g, '/').replace(/~0/g, '~');
        }
        exports.unescapeJsonPointer = unescapeJsonPointer;
        function eachItem(xs, f) {
          if (Array.isArray(xs)) {
            for (const x of xs) f(x);
          } else {
            f(xs);
          }
        }
        exports.eachItem = eachItem;
        function makeMergeEvaluated({ mergeNames, mergeToName, mergeValues, resultToName }) {
          return (gen, from, to, toName) => {
            const res = to === undefined
              ? from
              : to instanceof codegen_1.Name
                ? (from instanceof codegen_1.Name ? mergeNames(gen, from, to) : mergeToName(gen, from, to), to)
                : from instanceof codegen_1.Name
                  ? (mergeToName(gen, to, from), from)
                  : mergeValues(from, to);
            return toName === codegen_1.Name && !(res instanceof codegen_1.Name) ? resultToName(gen, res) : res;
          };
        }
        exports.mergeEvaluated = {
          props: makeMergeEvaluated({
            mergeNames: (gen, from, to) => gen.if((0, codegen_1._) `${to} !== true && ${from} !== undefined`, () => {
              gen.if((0, codegen_1._) `${from} === true`, () => gen.assign(to, true), () => gen.assign(to, (0, codegen_1._) `${to} || {}`).code((0, codegen_1._) `Object.assign(${to}, ${from})`));
            }),
            mergeToName: (gen, from, to) => gen.if((0, codegen_1._) `${to} !== true`, () => {
              if (from === true) {
                gen.assign(to, true);
              } else {
                gen.assign(to, (0, codegen_1._) `${to} || {}`);
                setEvaluated(gen, to, from);
              }
            }),
            mergeValues: (from, to) => (from === true ? true : { ...from, ...to }),
            resultToName: evaluatedPropsToName,
          }),
          items: makeMergeEvaluated({
            mergeNames: (gen, from, to) => gen.if((0, codegen_1._) `${to} !== true && ${from} !== undefined`, () => gen.assign(to, (0, codegen_1._) `${from} === true ? true : ${to} > ${from} ? ${to} : ${from}`)),
            mergeToName: (gen, from, to) => gen.if((0, codegen_1._) `${to} !== true`, () => gen.assign(to, from === true ? true : (0, codegen_1._) `${to} > ${from} ? ${to} : ${from}`)),
            mergeValues: (from, to) => (from === true ? true : Math.max(from, to)),
            resultToName: (gen, items) => gen.var('items', items),
          }),
        };
        function evaluatedPropsToName(gen, ps) {
          if (ps === true) return gen.var('props', true);
          const props = gen.var('props', (0, codegen_1._) `{}`);
          if (ps !== undefined) setEvaluated(gen, props, ps);
          return props;
        }
        exports.evaluatedPropsToName = evaluatedPropsToName;
        function setEvaluated(gen, props, ps) {
          Object.keys(ps).forEach(p => gen.assign((0, codegen_1._) `${props}${(0, codegen_1.getProperty)(p)}`, true));
        }
        exports.setEvaluated = setEvaluated;
        const snippets = {};
        function useFunc(gen, f) {
          return gen.scopeValue('func', {
            ref: f,
            code: snippets[f.code] || (snippets[f.code] = new code_1._Code(f.code)),
          });
        }
        exports.useFunc = useFunc;
        let Type;
        (function (Type) {
          Type[Type.Num = 0] = 'Num';
          Type[Type.Str = 1] = 'Str';
        }(Type = exports.Type || (exports.Type = {})));
        function getErrorPath(dataProp, dataPropType, jsPropertySyntax) {
          // let path
          if (dataProp instanceof codegen_1.Name) {
            const isNumber = dataPropType === Type.Num;
            return jsPropertySyntax
              ? isNumber
                ? (0, codegen_1._) `"[" + ${dataProp} + "]"`
                : (0, codegen_1._) `"['" + ${dataProp} + "']"`
              : isNumber
                ? (0, codegen_1._) `"/" + ${dataProp}`
                : (0, codegen_1._) `"/" + ${dataProp}.replace(/~/g, "~0").replace(/\\//g, "~1")`; // TODO maybe use global escapePointer
          }
          return jsPropertySyntax ? (0, codegen_1.getProperty)(dataProp).toString() : `/${escapeJsonPointer(dataProp)}`;
        }
        exports.getErrorPath = getErrorPath;
        function checkStrictMode(it, msg, mode = it.opts.strictSchema) {
          if (!mode) return;
          msg = `strict mode: ${msg}`;
          if (mode === true) throw new Error(msg);
          it.self.logger.warn(msg);
        }
        exports.checkStrictMode = checkStrictMode;
        // # sourceMappingURL=util.js.map
        /***/ }),

      /***/ 8876:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.shouldUseRule = exports.shouldUseGroup = exports.schemaHasRulesForType = void 0;
        function schemaHasRulesForType({ schema, self }, type) {
          const group = self.RULES.types[type];
          return group && group !== true && shouldUseGroup(schema, group);
        }
        exports.schemaHasRulesForType = schemaHasRulesForType;
        function shouldUseGroup(schema, group) {
          return group.rules.some(rule => shouldUseRule(schema, rule));
        }
        exports.shouldUseGroup = shouldUseGroup;
        function shouldUseRule(schema, rule) {
          let _a;
          return (schema[rule.keyword] !== undefined
        || ((_a = rule.definition.implements) === null || _a === void 0 ? void 0 : _a.some(kwd => schema[kwd] !== undefined)));
        }
        exports.shouldUseRule = shouldUseRule;
        // # sourceMappingURL=applicability.js.map
        /***/ }),

      /***/ 5667:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.boolOrEmptySchema = exports.topBoolOrEmptySchema = void 0;
        const errors_1 = __webpack_require__(4181);
        const codegen_1 = __webpack_require__(3487);
        const names_1 = __webpack_require__(2141);
        const boolError = {
          message: 'boolean schema is false',
        };
        function topBoolOrEmptySchema(it) {
          const { gen, schema, validateName } = it;
          if (schema === false) {
            falseSchemaError(it, false);
          } else if (typeof schema === 'object' && schema.$async === true) {
            gen.return(names_1.default.data);
          } else {
            gen.assign((0, codegen_1._) `${validateName}.errors`, null);
            gen.return(true);
          }
        }
        exports.topBoolOrEmptySchema = topBoolOrEmptySchema;
        function boolOrEmptySchema(it, valid) {
          const { gen, schema } = it;
          if (schema === false) {
            gen.var(valid, false); // TODO var
            falseSchemaError(it);
          } else {
            gen.var(valid, true); // TODO var
          }
        }
        exports.boolOrEmptySchema = boolOrEmptySchema;
        function falseSchemaError(it, overrideAllErrors) {
          const { gen, data } = it;
          // TODO maybe some other interface should be used for non-keyword validation errors...
          const cxt = {
            gen,
            keyword: 'false schema',
            data,
            schema: false,
            schemaCode: false,
            schemaValue: false,
            params: {},
            it,
          };
          (0, errors_1.reportError)(cxt, boolError, undefined, overrideAllErrors);
        }
        // # sourceMappingURL=boolSchema.js.map
        /***/ }),

      /***/ 453:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.reportTypeError = exports.checkDataTypes = exports.checkDataType = exports.coerceAndCheckDataType = exports.getJSONTypes = exports.getSchemaTypes = exports.DataType = void 0;
        const rules_1 = __webpack_require__(3141);
        const applicability_1 = __webpack_require__(8876);
        const errors_1 = __webpack_require__(4181);
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        let DataType;
        (function (DataType) {
          DataType[DataType.Correct = 0] = 'Correct';
          DataType[DataType.Wrong = 1] = 'Wrong';
        }(DataType = exports.DataType || (exports.DataType = {})));
        function getSchemaTypes(schema) {
          const types = getJSONTypes(schema.type);
          const hasNull = types.includes('null');
          if (hasNull) {
            if (schema.nullable === false) throw new Error('type: null contradicts nullable: false');
          } else {
            if (!types.length && schema.nullable !== undefined) {
              throw new Error('"nullable" cannot be used without "type"');
            }
            if (schema.nullable === true) types.push('null');
          }
          return types;
        }
        exports.getSchemaTypes = getSchemaTypes;
        function getJSONTypes(ts) {
          const types = Array.isArray(ts) ? ts : ts ? [ts] : [];
          if (types.every(rules_1.isJSONType)) return types;
          throw new Error(`type must be JSONType or JSONType[]: ${types.join(',')}`);
        }
        exports.getJSONTypes = getJSONTypes;
        function coerceAndCheckDataType(it, types) {
          const { gen, data, opts } = it;
          const coerceTo = coerceToTypes(types, opts.coerceTypes);
          const checkTypes = types.length > 0
        && !(coerceTo.length === 0 && types.length === 1 && (0, applicability_1.schemaHasRulesForType)(it, types[0]));
          if (checkTypes) {
            const wrongType = checkDataTypes(types, data, opts.strictNumbers, DataType.Wrong);
            gen.if(wrongType, () => {
              if (coerceTo.length) coerceData(it, types, coerceTo);
              else reportTypeError(it);
            });
          }
          return checkTypes;
        }
        exports.coerceAndCheckDataType = coerceAndCheckDataType;
        const COERCIBLE = new Set(['string', 'number', 'integer', 'boolean', 'null']);
        function coerceToTypes(types, coerceTypes) {
          return coerceTypes
            ? types.filter(t => COERCIBLE.has(t) || (coerceTypes === 'array' && t === 'array'))
            : [];
        }
        function coerceData(it, types, coerceTo) {
          const { gen, data, opts } = it;
          const dataType = gen.let('dataType', (0, codegen_1._) `typeof ${data}`);
          const coerced = gen.let('coerced', (0, codegen_1._) `undefined`);
          if (opts.coerceTypes === 'array') {
            gen.if((0, codegen_1._) `${dataType} == 'object' && Array.isArray(${data}) && ${data}.length == 1`, () => gen
              .assign(data, (0, codegen_1._) `${data}[0]`)
              .assign(dataType, (0, codegen_1._) `typeof ${data}`)
              .if(checkDataTypes(types, data, opts.strictNumbers), () => gen.assign(coerced, data)));
          }
          gen.if((0, codegen_1._) `${coerced} !== undefined`);
          for (const t of coerceTo) {
            if (COERCIBLE.has(t) || (t === 'array' && opts.coerceTypes === 'array')) {
              coerceSpecificType(t);
            }
          }
          gen.else();
          reportTypeError(it);
          gen.endIf();
          gen.if((0, codegen_1._) `${coerced} !== undefined`, () => {
            gen.assign(data, coerced);
            assignParentData(it, coerced);
          });
          function coerceSpecificType(t) {
            switch (t) {
              case 'string':
                gen
                  .elseIf((0, codegen_1._) `${dataType} == "number" || ${dataType} == "boolean"`)
                  .assign(coerced, (0, codegen_1._) `"" + ${data}`)
                  .elseIf((0, codegen_1._) `${data} === null`)
                  .assign(coerced, (0, codegen_1._) `""`);
                return;
              case 'number':
                gen
                  .elseIf((0, codegen_1._) `${dataType} == "boolean" || ${data} === null
              || (${dataType} == "string" && ${data} && ${data} == +${data})`)
                  .assign(coerced, (0, codegen_1._) `+${data}`);
                return;
              case 'integer':
                gen
                  .elseIf((0, codegen_1._) `${dataType} === "boolean" || ${data} === null
              || (${dataType} === "string" && ${data} && ${data} == +${data} && !(${data} % 1))`)
                  .assign(coerced, (0, codegen_1._) `+${data}`);
                return;
              case 'boolean':
                gen
                  .elseIf((0, codegen_1._) `${data} === "false" || ${data} === 0 || ${data} === null`)
                  .assign(coerced, false)
                  .elseIf((0, codegen_1._) `${data} === "true" || ${data} === 1`)
                  .assign(coerced, true);
                return;
              case 'null':
                gen.elseIf((0, codegen_1._) `${data} === "" || ${data} === 0 || ${data} === false`);
                gen.assign(coerced, null);
                return;
              case 'array':
                gen
                  .elseIf((0, codegen_1._) `${dataType} === "string" || ${dataType} === "number"
              || ${dataType} === "boolean" || ${data} === null`)
                  .assign(coerced, (0, codegen_1._) `[${data}]`);
            }
          }
        }
        function assignParentData({ gen, parentData, parentDataProperty }, expr) {
          // TODO use gen.property
          gen.if((0, codegen_1._) `${parentData} !== undefined`, () => gen.assign((0, codegen_1._) `${parentData}[${parentDataProperty}]`, expr));
        }
        function checkDataType(dataType, data, strictNums, correct = DataType.Correct) {
          const EQ = correct === DataType.Correct ? codegen_1.operators.EQ : codegen_1.operators.NEQ;
          let cond;
          switch (dataType) {
            case 'null':
              return (0, codegen_1._) `${data} ${EQ} null`;
            case 'array':
              cond = (0, codegen_1._) `Array.isArray(${data})`;
              break;
            case 'object':
              cond = (0, codegen_1._) `${data} && typeof ${data} == "object" && !Array.isArray(${data})`;
              break;
            case 'integer':
              cond = numCond((0, codegen_1._) `!(${data} % 1) && !isNaN(${data})`);
              break;
            case 'number':
              cond = numCond();
              break;
            default:
              return (0, codegen_1._) `typeof ${data} ${EQ} ${dataType}`;
          }
          return correct === DataType.Correct ? cond : (0, codegen_1.not)(cond);
          function numCond(_cond = codegen_1.nil) {
            return (0, codegen_1.and)((0, codegen_1._) `typeof ${data} == "number"`, _cond, strictNums ? (0, codegen_1._) `isFinite(${data})` : codegen_1.nil);
          }
        }
        exports.checkDataType = checkDataType;
        function checkDataTypes(dataTypes, data, strictNums, correct) {
          if (dataTypes.length === 1) {
            return checkDataType(dataTypes[0], data, strictNums, correct);
          }
          let cond;
          const types = (0, util_1.toHash)(dataTypes);
          if (types.array && types.object) {
            const notObj = (0, codegen_1._) `typeof ${data} != "object"`;
            cond = types.null ? notObj : (0, codegen_1._) `!${data} || ${notObj}`;
            delete types.null;
            delete types.array;
            delete types.object;
          } else {
            cond = codegen_1.nil;
          }
          if (types.number) delete types.integer;
          for (const t in types) cond = (0, codegen_1.and)(cond, checkDataType(t, data, strictNums, correct));
          return cond;
        }
        exports.checkDataTypes = checkDataTypes;
        const typeError = {
          message: ({ schema }) => `must be ${schema}`,
          params: ({ schema, schemaValue }) => (typeof schema === 'string' ? (0, codegen_1._) `{type: ${schema}}` : (0, codegen_1._) `{type: ${schemaValue}}`),
        };
        function reportTypeError(it) {
          const cxt = getTypeErrorContext(it);
          (0, errors_1.reportError)(cxt, typeError);
        }
        exports.reportTypeError = reportTypeError;
        function getTypeErrorContext(it) {
          const { gen, data, schema } = it;
          const schemaCode = (0, util_1.schemaRefOrVal)(it, schema, 'type');
          return {
            gen,
            keyword: 'type',
            data,
            schema: schema.type,
            schemaCode,
            schemaValue: schemaCode,
            parentSchema: schema,
            params: {},
            it,
          };
        }
        // # sourceMappingURL=dataType.js.map
        /***/ }),

      /***/ 313:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.assignDefaults = void 0;
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        function assignDefaults(it, ty) {
          const { properties, items } = it.schema;
          if (ty === 'object' && properties) {
            for (const key in properties) {
              assignDefault(it, key, properties[key].default);
            }
          } else if (ty === 'array' && Array.isArray(items)) {
            items.forEach((sch, i) => assignDefault(it, i, sch.default));
          }
        }
        exports.assignDefaults = assignDefaults;
        function assignDefault(it, prop, defaultValue) {
          const { gen, compositeRule, data, opts } = it;
          if (defaultValue === undefined) return;
          const childData = (0, codegen_1._) `${data}${(0, codegen_1.getProperty)(prop)}`;
          if (compositeRule) {
            (0, util_1.checkStrictMode)(it, `default is ignored for: ${childData}`);
            return;
          }
          let condition = (0, codegen_1._) `${childData} === undefined`;
          if (opts.useDefaults === 'empty') {
            condition = (0, codegen_1._) `${condition} || ${childData} === null || ${childData} === ""`;
          }
          // `${childData} === undefined` +
          // (opts.useDefaults === "empty" ? ` || ${childData} === null || ${childData} === ""` : "")
          gen.if(condition, (0, codegen_1._) `${childData} = ${(0, codegen_1.stringify)(defaultValue)}`);
        }
        // # sourceMappingURL=defaults.js.map
        /***/ }),

      /***/ 4815:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.getData = exports.KeywordCxt = exports.validateFunctionCode = void 0;
        const boolSchema_1 = __webpack_require__(5667);
        const dataType_1 = __webpack_require__(453);
        const applicability_1 = __webpack_require__(8876);
        const dataType_2 = __webpack_require__(453);
        const defaults_1 = __webpack_require__(313);
        const keyword_1 = __webpack_require__(5005);
        const subschema_1 = __webpack_require__(3099);
        const codegen_1 = __webpack_require__(3487);
        const names_1 = __webpack_require__(2141);
        const resolve_1 = __webpack_require__(2531);
        const util_1 = __webpack_require__(6776);
        const errors_1 = __webpack_require__(4181);
        // schema compilation - generates validation function, subschemaCode (below) is used for subschemas
        function validateFunctionCode(it) {
          if (isSchemaObj(it)) {
            checkKeywords(it);
            if (schemaCxtHasRules(it)) {
              topSchemaObjCode(it);
              return;
            }
          }
          validateFunction(it, () => (0, boolSchema_1.topBoolOrEmptySchema)(it));
        }
        exports.validateFunctionCode = validateFunctionCode;
        function validateFunction({ gen, validateName, schema, schemaEnv, opts }, body) {
          if (opts.code.es5) {
            gen.func(validateName, (0, codegen_1._) `${names_1.default.data}, ${names_1.default.valCxt}`, schemaEnv.$async, () => {
              gen.code((0, codegen_1._) `"use strict"; ${funcSourceUrl(schema, opts)}`);
              destructureValCxtES5(gen, opts);
              gen.code(body);
            });
          } else {
            gen.func(validateName, (0, codegen_1._) `${names_1.default.data}, ${destructureValCxt(opts)}`, schemaEnv.$async, () => gen.code(funcSourceUrl(schema, opts)).code(body));
          }
        }
        function destructureValCxt(opts) {
          return (0, codegen_1._) `{${names_1.default.instancePath}="", ${names_1.default.parentData}, ${names_1.default.parentDataProperty}, ${names_1.default.rootData}=${names_1.default.data}${opts.dynamicRef ? (0, codegen_1._) `, ${names_1.default.dynamicAnchors}={}` : codegen_1.nil}}={}`;
        }
        function destructureValCxtES5(gen, opts) {
          gen.if(names_1.default.valCxt, () => {
            gen.var(names_1.default.instancePath, (0, codegen_1._) `${names_1.default.valCxt}.${names_1.default.instancePath}`);
            gen.var(names_1.default.parentData, (0, codegen_1._) `${names_1.default.valCxt}.${names_1.default.parentData}`);
            gen.var(names_1.default.parentDataProperty, (0, codegen_1._) `${names_1.default.valCxt}.${names_1.default.parentDataProperty}`);
            gen.var(names_1.default.rootData, (0, codegen_1._) `${names_1.default.valCxt}.${names_1.default.rootData}`);
            if (opts.dynamicRef) gen.var(names_1.default.dynamicAnchors, (0, codegen_1._) `${names_1.default.valCxt}.${names_1.default.dynamicAnchors}`);
          }, () => {
            gen.var(names_1.default.instancePath, (0, codegen_1._) `""`);
            gen.var(names_1.default.parentData, (0, codegen_1._) `undefined`);
            gen.var(names_1.default.parentDataProperty, (0, codegen_1._) `undefined`);
            gen.var(names_1.default.rootData, names_1.default.data);
            if (opts.dynamicRef) gen.var(names_1.default.dynamicAnchors, (0, codegen_1._) `{}`);
          });
        }
        function topSchemaObjCode(it) {
          const { schema, opts, gen } = it;
          validateFunction(it, () => {
            if (opts.$comment && schema.$comment) commentKeyword(it);
            checkNoDefault(it);
            gen.let(names_1.default.vErrors, null);
            gen.let(names_1.default.errors, 0);
            if (opts.unevaluated) resetEvaluated(it);
            typeAndKeywords(it);
            returnResults(it);
          });
          return;
        }
        function resetEvaluated(it) {
          // TODO maybe some hook to execute it in the end to check whether props/items are Name, as in assignEvaluated
          const { gen, validateName } = it;
          it.evaluated = gen.const('evaluated', (0, codegen_1._) `${validateName}.evaluated`);
          gen.if((0, codegen_1._) `${it.evaluated}.dynamicProps`, () => gen.assign((0, codegen_1._) `${it.evaluated}.props`, (0, codegen_1._) `undefined`));
          gen.if((0, codegen_1._) `${it.evaluated}.dynamicItems`, () => gen.assign((0, codegen_1._) `${it.evaluated}.items`, (0, codegen_1._) `undefined`));
        }
        function funcSourceUrl(schema, opts) {
          const schId = typeof schema === 'object' && schema[opts.schemaId];
          return schId && (opts.code.source || opts.code.process) ? (0, codegen_1._) `/*# sourceURL=${schId} */` : codegen_1.nil;
        }
        // schema compilation - this function is used recursively to generate code for sub-schemas
        function subschemaCode(it, valid) {
          if (isSchemaObj(it)) {
            checkKeywords(it);
            if (schemaCxtHasRules(it)) {
              subSchemaObjCode(it, valid);
              return;
            }
          }
          (0, boolSchema_1.boolOrEmptySchema)(it, valid);
        }
        function schemaCxtHasRules({ schema, self }) {
          if (typeof schema === 'boolean') return !schema;
          for (const key in schema) if (self.RULES.all[key]) return true;
          return false;
        }
        function isSchemaObj(it) {
          return typeof it.schema !== 'boolean';
        }
        function subSchemaObjCode(it, valid) {
          const { schema, gen, opts } = it;
          if (opts.$comment && schema.$comment) commentKeyword(it);
          updateContext(it);
          checkAsyncSchema(it);
          const errsCount = gen.const('_errs', names_1.default.errors);
          typeAndKeywords(it, errsCount);
          // TODO var
          gen.var(valid, (0, codegen_1._) `${errsCount} === ${names_1.default.errors}`);
        }
        function checkKeywords(it) {
          (0, util_1.checkUnknownRules)(it);
          checkRefsAndKeywords(it);
        }
        function typeAndKeywords(it, errsCount) {
          if (it.opts.jtd) return schemaKeywords(it, [], false, errsCount);
          const types = (0, dataType_1.getSchemaTypes)(it.schema);
          const checkedTypes = (0, dataType_1.coerceAndCheckDataType)(it, types);
          schemaKeywords(it, types, !checkedTypes, errsCount);
        }
        function checkRefsAndKeywords(it) {
          const { schema, errSchemaPath, opts, self } = it;
          if (schema.$ref && opts.ignoreKeywordsWithRef && (0, util_1.schemaHasRulesButRef)(schema, self.RULES)) {
            self.logger.warn(`$ref: keywords ignored in schema at path "${errSchemaPath}"`);
          }
        }
        function checkNoDefault(it) {
          const { schema, opts } = it;
          if (schema.default !== undefined && opts.useDefaults && opts.strictSchema) {
            (0, util_1.checkStrictMode)(it, 'default is ignored in the schema root');
          }
        }
        function updateContext(it) {
          const schId = it.schema[it.opts.schemaId];
          if (schId) it.baseId = (0, resolve_1.resolveUrl)(it.opts.uriResolver, it.baseId, schId);
        }
        function checkAsyncSchema(it) {
          if (it.schema.$async && !it.schemaEnv.$async) throw new Error('async schema in sync schema');
        }
        function commentKeyword({ gen, schemaEnv, schema, errSchemaPath, opts }) {
          const msg = schema.$comment;
          if (opts.$comment === true) {
            gen.code((0, codegen_1._) `${names_1.default.self}.logger.log(${msg})`);
          } else if (typeof opts.$comment === 'function') {
            const schemaPath = (0, codegen_1.str) `${errSchemaPath}/$comment`;
            const rootName = gen.scopeValue('root', { ref: schemaEnv.root });
            gen.code((0, codegen_1._) `${names_1.default.self}.opts.$comment(${msg}, ${schemaPath}, ${rootName}.schema)`);
          }
        }
        function returnResults(it) {
          const { gen, schemaEnv, validateName, ValidationError, opts } = it;
          if (schemaEnv.$async) {
            // TODO assign unevaluated
            gen.if((0, codegen_1._) `${names_1.default.errors} === 0`, () => gen.return(names_1.default.data), () => gen.throw((0, codegen_1._) `new ${ValidationError}(${names_1.default.vErrors})`));
          } else {
            gen.assign((0, codegen_1._) `${validateName}.errors`, names_1.default.vErrors);
            if (opts.unevaluated) assignEvaluated(it);
            gen.return((0, codegen_1._) `${names_1.default.errors} === 0`);
          }
        }
        function assignEvaluated({ gen, evaluated, props, items }) {
          if (props instanceof codegen_1.Name) gen.assign((0, codegen_1._) `${evaluated}.props`, props);
          if (items instanceof codegen_1.Name) gen.assign((0, codegen_1._) `${evaluated}.items`, items);
        }
        function schemaKeywords(it, types, typeErrors, errsCount) {
          const { gen, schema, data, allErrors, opts, self } = it;
          const { RULES } = self;
          if (schema.$ref && (opts.ignoreKeywordsWithRef || !(0, util_1.schemaHasRulesButRef)(schema, RULES))) {
            gen.block(() => keywordCode(it, '$ref', RULES.all.$ref.definition)); // TODO typecast
            return;
          }
          if (!opts.jtd) checkStrictTypes(it, types);
          gen.block(() => {
            for (const group of RULES.rules) groupKeywords(group);
            groupKeywords(RULES.post);
          });
          function groupKeywords(group) {
            if (!(0, applicability_1.shouldUseGroup)(schema, group)) return;
            if (group.type) {
              gen.if((0, dataType_2.checkDataType)(group.type, data, opts.strictNumbers));
              iterateKeywords(it, group);
              if (types.length === 1 && types[0] === group.type && typeErrors) {
                gen.else();
                (0, dataType_2.reportTypeError)(it);
              }
              gen.endIf();
            } else {
              iterateKeywords(it, group);
            }
            // TODO make it "ok" call?
            if (!allErrors) gen.if((0, codegen_1._) `${names_1.default.errors} === ${errsCount || 0}`);
          }
        }
        function iterateKeywords(it, group) {
          const { gen, schema, opts: { useDefaults } } = it;
          if (useDefaults) (0, defaults_1.assignDefaults)(it, group.type);
          gen.block(() => {
            for (const rule of group.rules) {
              if ((0, applicability_1.shouldUseRule)(schema, rule)) {
                keywordCode(it, rule.keyword, rule.definition, group.type);
              }
            }
          });
        }
        function checkStrictTypes(it, types) {
          if (it.schemaEnv.meta || !it.opts.strictTypes) return;
          checkContextTypes(it, types);
          if (!it.opts.allowUnionTypes) checkMultipleTypes(it, types);
          checkKeywordTypes(it, it.dataTypes);
        }
        function checkContextTypes(it, types) {
          if (!types.length) return;
          if (!it.dataTypes.length) {
            it.dataTypes = types;
            return;
          }
          types.forEach((t) => {
            if (!includesType(it.dataTypes, t)) {
              strictTypesError(it, `type "${t}" not allowed by context "${it.dataTypes.join(',')}"`);
            }
          });
          narrowSchemaTypes(it, types);
        }
        function checkMultipleTypes(it, ts) {
          if (ts.length > 1 && !(ts.length === 2 && ts.includes('null'))) {
            strictTypesError(it, 'use allowUnionTypes to allow union type keyword');
          }
        }
        function checkKeywordTypes(it, ts) {
          const rules = it.self.RULES.all;
          for (const keyword in rules) {
            const rule = rules[keyword];
            if (typeof rule === 'object' && (0, applicability_1.shouldUseRule)(it.schema, rule)) {
              const { type } = rule.definition;
              if (type.length && !type.some(t => hasApplicableType(ts, t))) {
                strictTypesError(it, `missing type "${type.join(',')}" for keyword "${keyword}"`);
              }
            }
          }
        }
        function hasApplicableType(schTs, kwdT) {
          return schTs.includes(kwdT) || (kwdT === 'number' && schTs.includes('integer'));
        }
        function includesType(ts, t) {
          return ts.includes(t) || (t === 'integer' && ts.includes('number'));
        }
        function narrowSchemaTypes(it, withTypes) {
          const ts = [];
          for (const t of it.dataTypes) {
            if (includesType(withTypes, t)) ts.push(t);
            else if (withTypes.includes('integer') && t === 'number') ts.push('integer');
          }
          it.dataTypes = ts;
        }
        function strictTypesError(it, msg) {
          const schemaPath = it.schemaEnv.baseId + it.errSchemaPath;
          msg += ` at "${schemaPath}" (strictTypes)`;
          (0, util_1.checkStrictMode)(it, msg, it.opts.strictTypes);
        }
        class KeywordCxt {
          constructor(it, def, keyword) {
            (0, keyword_1.validateKeywordUsage)(it, def, keyword);
            this.gen = it.gen;
            this.allErrors = it.allErrors;
            this.keyword = keyword;
            this.data = it.data;
            this.schema = it.schema[keyword];
            this.$data = def.$data && it.opts.$data && this.schema && this.schema.$data;
            this.schemaValue = (0, util_1.schemaRefOrVal)(it, this.schema, keyword, this.$data);
            this.schemaType = def.schemaType;
            this.parentSchema = it.schema;
            this.params = {};
            this.it = it;
            this.def = def;
            if (this.$data) {
              this.schemaCode = it.gen.const('vSchema', getData(this.$data, it));
            } else {
              this.schemaCode = this.schemaValue;
              if (!(0, keyword_1.validSchemaType)(this.schema, def.schemaType, def.allowUndefined)) {
                throw new Error(`${keyword} value must be ${JSON.stringify(def.schemaType)}`);
              }
            }
            if ('code' in def ? def.trackErrors : def.errors !== false) {
              this.errsCount = it.gen.const('_errs', names_1.default.errors);
            }
          }
          result(condition, successAction, failAction) {
            this.failResult((0, codegen_1.not)(condition), successAction, failAction);
          }
          failResult(condition, successAction, failAction) {
            this.gen.if(condition);
            if (failAction) failAction();
            else this.error();
            if (successAction) {
              this.gen.else();
              successAction();
              if (this.allErrors) this.gen.endIf();
            } else {
              if (this.allErrors) this.gen.endIf();
              else this.gen.else();
            }
          }
          pass(condition, failAction) {
            this.failResult((0, codegen_1.not)(condition), undefined, failAction);
          }
          fail(condition) {
            if (condition === undefined) {
              this.error();
              if (!this.allErrors) this.gen.if(false); // this branch will be removed by gen.optimize
              return;
            }
            this.gen.if(condition);
            this.error();
            if (this.allErrors) this.gen.endIf();
            else this.gen.else();
          }
          fail$data(condition) {
            if (!this.$data) return this.fail(condition);
            const { schemaCode } = this;
            this.fail((0, codegen_1._) `${schemaCode} !== undefined && (${(0, codegen_1.or)(this.invalid$data(), condition)})`);
          }
          error(append, errorParams, errorPaths) {
            if (errorParams) {
              this.setParams(errorParams);
              this._error(append, errorPaths);
              this.setParams({});
              return;
            }
            this._error(append, errorPaths);
          }
          _error(append, errorPaths) {
            ;
            (append ? errors_1.reportExtraError : errors_1.reportError)(this, this.def.error, errorPaths);
          }
          $dataError() {
            (0, errors_1.reportError)(this, this.def.$dataError || errors_1.keyword$DataError);
          }
          reset() {
            if (this.errsCount === undefined) throw new Error('add "trackErrors" to keyword definition');
            (0, errors_1.resetErrorsCount)(this.gen, this.errsCount);
          }
          ok(cond) {
            if (!this.allErrors) this.gen.if(cond);
          }
          setParams(obj, assign) {
            if (assign) Object.assign(this.params, obj);
            else this.params = obj;
          }
          block$data(valid, codeBlock, $dataValid = codegen_1.nil) {
            this.gen.block(() => {
              this.check$data(valid, $dataValid);
              codeBlock();
            });
          }
          check$data(valid = codegen_1.nil, $dataValid = codegen_1.nil) {
            if (!this.$data) return;
            const { gen, schemaCode, schemaType, def } = this;
            gen.if((0, codegen_1.or)((0, codegen_1._) `${schemaCode} === undefined`, $dataValid));
            if (valid !== codegen_1.nil) gen.assign(valid, true);
            if (schemaType.length || def.validateSchema) {
              gen.elseIf(this.invalid$data());
              this.$dataError();
              if (valid !== codegen_1.nil) gen.assign(valid, false);
            }
            gen.else();
          }
          invalid$data() {
            const { gen, schemaCode, schemaType, def, it } = this;
            return (0, codegen_1.or)(wrong$DataType(), invalid$DataSchema());
            function wrong$DataType() {
              if (schemaType.length) {
                /* istanbul ignore if */
                if (!(schemaCode instanceof codegen_1.Name)) throw new Error('ajv implementation error');
                const st = Array.isArray(schemaType) ? schemaType : [schemaType];
                return (0, codegen_1._) `${(0, dataType_2.checkDataTypes)(st, schemaCode, it.opts.strictNumbers, dataType_2.DataType.Wrong)}`;
              }
              return codegen_1.nil;
            }
            function invalid$DataSchema() {
              if (def.validateSchema) {
                const validateSchemaRef = gen.scopeValue('validate$data', { ref: def.validateSchema }); // TODO value.code for standalone
                return (0, codegen_1._) `!${validateSchemaRef}(${schemaCode})`;
              }
              return codegen_1.nil;
            }
          }
          subschema(appl, valid) {
            const subschema = (0, subschema_1.getSubschema)(this.it, appl);
            (0, subschema_1.extendSubschemaData)(subschema, this.it, appl);
            (0, subschema_1.extendSubschemaMode)(subschema, appl);
            const nextContext = { ...this.it, ...subschema, items: undefined, props: undefined };
            subschemaCode(nextContext, valid);
            return nextContext;
          }
          mergeEvaluated(schemaCxt, toName) {
            const { it, gen } = this;
            if (!it.opts.unevaluated) return;
            if (it.props !== true && schemaCxt.props !== undefined) {
              it.props = util_1.mergeEvaluated.props(gen, schemaCxt.props, it.props, toName);
            }
            if (it.items !== true && schemaCxt.items !== undefined) {
              it.items = util_1.mergeEvaluated.items(gen, schemaCxt.items, it.items, toName);
            }
          }
          mergeValidEvaluated(schemaCxt, valid) {
            const { it, gen } = this;
            if (it.opts.unevaluated && (it.props !== true || it.items !== true)) {
              gen.if(valid, () => this.mergeEvaluated(schemaCxt, codegen_1.Name));
              return true;
            }
          }
        }
        exports.KeywordCxt = KeywordCxt;
        function keywordCode(it, keyword, def, ruleType) {
          const cxt = new KeywordCxt(it, def, keyword);
          if ('code' in def) {
            def.code(cxt, ruleType);
          } else if (cxt.$data && def.validate) {
            (0, keyword_1.funcKeywordCode)(cxt, def);
          } else if ('macro' in def) {
            (0, keyword_1.macroKeywordCode)(cxt, def);
          } else if (def.compile || def.validate) {
            (0, keyword_1.funcKeywordCode)(cxt, def);
          }
        }
        const JSON_POINTER = /^\/(?:[^~]|~0|~1)*$/;
        const RELATIVE_JSON_POINTER = /^([0-9]+)(#|\/(?:[^~]|~0|~1)*)?$/;
        function getData($data, { dataLevel, dataNames, dataPathArr }) {
          let jsonPointer;
          let data;
          if ($data === '') return names_1.default.rootData;
          if ($data[0] === '/') {
            if (!JSON_POINTER.test($data)) throw new Error(`Invalid JSON-pointer: ${$data}`);
            jsonPointer = $data;
            data = names_1.default.rootData;
          } else {
            const matches = RELATIVE_JSON_POINTER.exec($data);
            if (!matches) throw new Error(`Invalid JSON-pointer: ${$data}`);
            const up = +matches[1];
            jsonPointer = matches[2];
            if (jsonPointer === '#') {
              if (up >= dataLevel) throw new Error(errorMsg('property/index', up));
              return dataPathArr[dataLevel - up];
            }
            if (up > dataLevel) throw new Error(errorMsg('data', up));
            data = dataNames[dataLevel - up];
            if (!jsonPointer) return data;
          }
          let expr = data;
          const segments = jsonPointer.split('/');
          for (const segment of segments) {
            if (segment) {
              data = (0, codegen_1._) `${data}${(0, codegen_1.getProperty)((0, util_1.unescapeJsonPointer)(segment))}`;
              expr = (0, codegen_1._) `${expr} && ${data}`;
            }
          }
          return expr;
          function errorMsg(pointerType, up) {
            return `Cannot access ${pointerType} ${up} levels up, current level is ${dataLevel}`;
          }
        }
        exports.getData = getData;
        // # sourceMappingURL=index.js.map
        /***/ }),

      /***/ 5005:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.validateKeywordUsage = exports.validSchemaType = exports.funcKeywordCode = exports.macroKeywordCode = void 0;
        const codegen_1 = __webpack_require__(3487);
        const names_1 = __webpack_require__(2141);
        const code_1 = __webpack_require__(412);
        const errors_1 = __webpack_require__(4181);
        function macroKeywordCode(cxt, def) {
          const { gen, keyword, schema, parentSchema, it } = cxt;
          const macroSchema = def.macro.call(it.self, schema, parentSchema, it);
          const schemaRef = useKeyword(gen, keyword, macroSchema);
          if (it.opts.validateSchema !== false) it.self.validateSchema(macroSchema, true);
          const valid = gen.name('valid');
          cxt.subschema({
            schema: macroSchema,
            schemaPath: codegen_1.nil,
            errSchemaPath: `${it.errSchemaPath}/${keyword}`,
            topSchemaRef: schemaRef,
            compositeRule: true,
          }, valid);
          cxt.pass(valid, () => cxt.error(true));
        }
        exports.macroKeywordCode = macroKeywordCode;
        function funcKeywordCode(cxt, def) {
          let _a;
          const { gen, keyword, schema, parentSchema, $data, it } = cxt;
          checkAsyncKeyword(it, def);
          const validate = !$data && def.compile ? def.compile.call(it.self, schema, parentSchema, it) : def.validate;
          const validateRef = useKeyword(gen, keyword, validate);
          const valid = gen.let('valid');
          cxt.block$data(valid, validateKeyword);
          cxt.ok((_a = def.valid) !== null && _a !== void 0 ? _a : valid);
          function validateKeyword() {
            if (def.errors === false) {
              assignValid();
              if (def.modifying) modifyData(cxt);
              reportErrs(() => cxt.error());
            } else {
              const ruleErrs = def.async ? validateAsync() : validateSync();
              if (def.modifying) modifyData(cxt);
              reportErrs(() => addErrs(cxt, ruleErrs));
            }
          }
          function validateAsync() {
            const ruleErrs = gen.let('ruleErrs', null);
            gen.try(() => assignValid((0, codegen_1._) `await `), e => gen.assign(valid, false).if((0, codegen_1._) `${e} instanceof ${it.ValidationError}`, () => gen.assign(ruleErrs, (0, codegen_1._) `${e}.errors`), () => gen.throw(e)));
            return ruleErrs;
          }
          function validateSync() {
            const validateErrs = (0, codegen_1._) `${validateRef}.errors`;
            gen.assign(validateErrs, null);
            assignValid(codegen_1.nil);
            return validateErrs;
          }
          function assignValid(_await = def.async ? (0, codegen_1._) `await ` : codegen_1.nil) {
            const passCxt = it.opts.passContext ? names_1.default.this : names_1.default.self;
            const passSchema = !(('compile' in def && !$data) || def.schema === false);
            gen.assign(valid, (0, codegen_1._) `${_await}${(0, code_1.callValidateCode)(cxt, validateRef, passCxt, passSchema)}`, def.modifying);
          }
          function reportErrs(errors) {
            let _a;
            gen.if((0, codegen_1.not)((_a = def.valid) !== null && _a !== void 0 ? _a : valid), errors);
          }
        }
        exports.funcKeywordCode = funcKeywordCode;
        function modifyData(cxt) {
          const { gen, data, it } = cxt;
          gen.if(it.parentData, () => gen.assign(data, (0, codegen_1._) `${it.parentData}[${it.parentDataProperty}]`));
        }
        function addErrs(cxt, errs) {
          const { gen } = cxt;
          gen.if((0, codegen_1._) `Array.isArray(${errs})`, () => {
            gen
              .assign(names_1.default.vErrors, (0, codegen_1._) `${names_1.default.vErrors} === null ? ${errs} : ${names_1.default.vErrors}.concat(${errs})`)
              .assign(names_1.default.errors, (0, codegen_1._) `${names_1.default.vErrors}.length`);
            (0, errors_1.extendErrors)(cxt);
          }, () => cxt.error());
        }
        function checkAsyncKeyword({ schemaEnv }, def) {
          if (def.async && !schemaEnv.$async) throw new Error('async keyword in sync schema');
        }
        function useKeyword(gen, keyword, result) {
          if (result === undefined) throw new Error(`keyword "${keyword}" failed to compile`);
          return gen.scopeValue('keyword', typeof result === 'function' ? { ref: result } : { ref: result, code: (0, codegen_1.stringify)(result) });
        }
        function validSchemaType(schema, schemaType, allowUndefined = false) {
          // TODO add tests
          return (!schemaType.length
        || schemaType.some(st => (st === 'array'
          ? Array.isArray(schema)
          : st === 'object'
            ? schema && typeof schema === 'object' && !Array.isArray(schema)
            : typeof schema === st || (allowUndefined && typeof schema === 'undefined'))));
        }
        exports.validSchemaType = validSchemaType;
        function validateKeywordUsage({ schema, opts, self, errSchemaPath }, def, keyword) {
          /* istanbul ignore if */
          if (Array.isArray(def.keyword) ? !def.keyword.includes(keyword) : def.keyword !== keyword) {
            throw new Error('ajv implementation error');
          }
          const deps = def.dependencies;
          if (deps === null || deps === void 0 ? void 0 : deps.some(kwd => !Object.prototype.hasOwnProperty.call(schema, kwd))) {
            throw new Error(`parent schema must have dependencies of ${keyword}: ${deps.join(',')}`);
          }
          if (def.validateSchema) {
            const valid = def.validateSchema(schema[keyword]);
            if (!valid) {
              const msg = `keyword "${keyword}" value is invalid at path "${errSchemaPath}": ${
                self.errorsText(def.validateSchema.errors)}`;
              if (opts.validateSchema === 'log') self.logger.error(msg);
              else throw new Error(msg);
            }
          }
        }
        exports.validateKeywordUsage = validateKeywordUsage;
        // # sourceMappingURL=keyword.js.map
        /***/ }),

      /***/ 3099:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.extendSubschemaMode = exports.extendSubschemaData = exports.getSubschema = void 0;
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        function getSubschema(it, { keyword, schemaProp, schema, schemaPath, errSchemaPath, topSchemaRef }) {
          if (keyword !== undefined && schema !== undefined) {
            throw new Error('both "keyword" and "schema" passed, only one allowed');
          }
          if (keyword !== undefined) {
            const sch = it.schema[keyword];
            return schemaProp === undefined
              ? {
                schema: sch,
                schemaPath: (0, codegen_1._) `${it.schemaPath}${(0, codegen_1.getProperty)(keyword)}`,
                errSchemaPath: `${it.errSchemaPath}/${keyword}`,
              }
              : {
                schema: sch[schemaProp],
                schemaPath: (0, codegen_1._) `${it.schemaPath}${(0, codegen_1.getProperty)(keyword)}${(0, codegen_1.getProperty)(schemaProp)}`,
                errSchemaPath: `${it.errSchemaPath}/${keyword}/${(0, util_1.escapeFragment)(schemaProp)}`,
              };
          }
          if (schema !== undefined) {
            if (schemaPath === undefined || errSchemaPath === undefined || topSchemaRef === undefined) {
              throw new Error('"schemaPath", "errSchemaPath" and "topSchemaRef" are required with "schema"');
            }
            return {
              schema,
              schemaPath,
              topSchemaRef,
              errSchemaPath,
            };
          }
          throw new Error('either "keyword" or "schema" must be passed');
        }
        exports.getSubschema = getSubschema;
        function extendSubschemaData(subschema, it, { dataProp, dataPropType: dpType, data, dataTypes, propertyName }) {
          if (data !== undefined && dataProp !== undefined) {
            throw new Error('both "data" and "dataProp" passed, only one allowed');
          }
          const { gen } = it;
          if (dataProp !== undefined) {
            const { errorPath, dataPathArr, opts } = it;
            const nextData = gen.let('data', (0, codegen_1._) `${it.data}${(0, codegen_1.getProperty)(dataProp)}`, true);
            dataContextProps(nextData);
            subschema.errorPath = (0, codegen_1.str) `${errorPath}${(0, util_1.getErrorPath)(dataProp, dpType, opts.jsPropertySyntax)}`;
            subschema.parentDataProperty = (0, codegen_1._) `${dataProp}`;
            subschema.dataPathArr = [...dataPathArr, subschema.parentDataProperty];
          }
          if (data !== undefined) {
            const nextData = data instanceof codegen_1.Name ? data : gen.let('data', data, true); // replaceable if used once?
            dataContextProps(nextData);
            if (propertyName !== undefined) subschema.propertyName = propertyName;
            // TODO something is possibly wrong here with not changing parentDataProperty and not appending dataPathArr
          }
          if (dataTypes) subschema.dataTypes = dataTypes;
          function dataContextProps(_nextData) {
            subschema.data = _nextData;
            subschema.dataLevel = it.dataLevel + 1;
            subschema.dataTypes = [];
            it.definedProperties = new Set();
            subschema.parentData = it.data;
            subschema.dataNames = [...it.dataNames, _nextData];
          }
        }
        exports.extendSubschemaData = extendSubschemaData;
        function extendSubschemaMode(subschema, { jtdDiscriminator, jtdMetadata, compositeRule, createErrors, allErrors }) {
          if (compositeRule !== undefined) subschema.compositeRule = compositeRule;
          if (createErrors !== undefined) subschema.createErrors = createErrors;
          if (allErrors !== undefined) subschema.allErrors = allErrors;
          subschema.jtdDiscriminator = jtdDiscriminator; // not inherited
          subschema.jtdMetadata = jtdMetadata; // not inherited
        }
        exports.extendSubschemaMode = extendSubschemaMode;
        // # sourceMappingURL=subschema.js.map
        /***/ }),

      /***/ 7159:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.CodeGen = exports.Name = exports.nil = exports.stringify = exports.str = exports._ = exports.KeywordCxt = void 0;
        const validate_1 = __webpack_require__(4815);
        Object.defineProperty(exports, 'KeywordCxt', ({ enumerable: true, get() {
          return validate_1.KeywordCxt;
        } }));
        const codegen_1 = __webpack_require__(3487);
        Object.defineProperty(exports, '_', ({ enumerable: true, get() {
          return codegen_1._;
        } }));
        Object.defineProperty(exports, 'str', ({ enumerable: true, get() {
          return codegen_1.str;
        } }));
        Object.defineProperty(exports, 'stringify', ({ enumerable: true, get() {
          return codegen_1.stringify;
        } }));
        Object.defineProperty(exports, 'nil', ({ enumerable: true, get() {
          return codegen_1.nil;
        } }));
        Object.defineProperty(exports, 'Name', ({ enumerable: true, get() {
          return codegen_1.Name;
        } }));
        Object.defineProperty(exports, 'CodeGen', ({ enumerable: true, get() {
          return codegen_1.CodeGen;
        } }));
        const validation_error_1 = __webpack_require__(7426);
        const ref_error_1 = __webpack_require__(6646);
        const rules_1 = __webpack_require__(3141);
        const compile_1 = __webpack_require__(5173);
        const codegen_2 = __webpack_require__(3487);
        const resolve_1 = __webpack_require__(2531);
        const dataType_1 = __webpack_require__(453);
        const util_1 = __webpack_require__(6776);
        const $dataRefSchema = __webpack_require__(4775);
        const uri_1 = __webpack_require__(3589);
        const defaultRegExp = (str, flags) => new RegExp(str, flags);
        defaultRegExp.code = 'new RegExp';
        const META_IGNORE_OPTIONS = ['removeAdditional', 'useDefaults', 'coerceTypes'];
        const EXT_SCOPE_NAMES = new Set([
          'validate',
          'serialize',
          'parse',
          'wrapper',
          'root',
          'schema',
          'keyword',
          'pattern',
          'formats',
          'validate$data',
          'func',
          'obj',
          'Error',
        ]);
        const removedOptions = {
          errorDataPath: '',
          format: '`validateFormats: false` can be used instead.',
          nullable: '"nullable" keyword is supported by default.',
          jsonPointers: 'Deprecated jsPropertySyntax can be used instead.',
          extendRefs: 'Deprecated ignoreKeywordsWithRef can be used instead.',
          missingRefs: 'Pass empty schema with $id that should be ignored to ajv.addSchema.',
          processCode: 'Use option `code: {process: (code, schemaEnv: object) => string}`',
          sourceCode: 'Use option `code: {source: true}`',
          strictDefaults: 'It is default now, see option `strict`.',
          strictKeywords: 'It is default now, see option `strict`.',
          uniqueItems: '"uniqueItems" keyword is always validated.',
          unknownFormats: 'Disable strict mode or pass `true` to `ajv.addFormat` (or `formats` option).',
          cache: 'Map is used as cache, schema object as key.',
          serialize: 'Map is used as cache, schema object as key.',
          ajvErrors: 'It is default now.',
        };
        const deprecatedOptions = {
          ignoreKeywordsWithRef: '',
          jsPropertySyntax: '',
          unicode: '"minLength"/"maxLength" account for unicode characters by default.',
        };
        const MAX_EXPRESSION = 200;
        // eslint-disable-next-line complexity
        function requiredOptions(o) {
          let _a; let _b; let _c; let _d; let _e; let _f; let _g; let _h; let _j; let _k; let _l; let _m; let _o; let _p; let _q; let _r; let _s; let _t; let _u; let _v; let _w; let _x; let _y; let _z; let _0;
          const s = o.strict;
          const _optz = (_a = o.code) === null || _a === void 0 ? void 0 : _a.optimize;
          const optimize = _optz === true || _optz === undefined ? 1 : _optz || 0;
          const regExp = (_c = (_b = o.code) === null || _b === void 0 ? void 0 : _b.regExp) !== null && _c !== void 0 ? _c : defaultRegExp;
          const uriResolver = (_d = o.uriResolver) !== null && _d !== void 0 ? _d : uri_1.default;
          return {
            strictSchema: (_f = (_e = o.strictSchema) !== null && _e !== void 0 ? _e : s) !== null && _f !== void 0 ? _f : true,
            strictNumbers: (_h = (_g = o.strictNumbers) !== null && _g !== void 0 ? _g : s) !== null && _h !== void 0 ? _h : true,
            strictTypes: (_k = (_j = o.strictTypes) !== null && _j !== void 0 ? _j : s) !== null && _k !== void 0 ? _k : 'log',
            strictTuples: (_m = (_l = o.strictTuples) !== null && _l !== void 0 ? _l : s) !== null && _m !== void 0 ? _m : 'log',
            strictRequired: (_p = (_o = o.strictRequired) !== null && _o !== void 0 ? _o : s) !== null && _p !== void 0 ? _p : false,
            code: o.code ? { ...o.code, optimize, regExp } : { optimize, regExp },
            loopRequired: (_q = o.loopRequired) !== null && _q !== void 0 ? _q : MAX_EXPRESSION,
            loopEnum: (_r = o.loopEnum) !== null && _r !== void 0 ? _r : MAX_EXPRESSION,
            meta: (_s = o.meta) !== null && _s !== void 0 ? _s : true,
            messages: (_t = o.messages) !== null && _t !== void 0 ? _t : true,
            inlineRefs: (_u = o.inlineRefs) !== null && _u !== void 0 ? _u : true,
            schemaId: (_v = o.schemaId) !== null && _v !== void 0 ? _v : '$id',
            addUsedSchema: (_w = o.addUsedSchema) !== null && _w !== void 0 ? _w : true,
            validateSchema: (_x = o.validateSchema) !== null && _x !== void 0 ? _x : true,
            validateFormats: (_y = o.validateFormats) !== null && _y !== void 0 ? _y : true,
            unicodeRegExp: (_z = o.unicodeRegExp) !== null && _z !== void 0 ? _z : true,
            int32range: (_0 = o.int32range) !== null && _0 !== void 0 ? _0 : true,
            uriResolver,
          };
        }
        class Ajv {
          constructor(opts = {}) {
            this.schemas = {};
            this.refs = {};
            this.formats = {};
            this._compilations = new Set();
            this._loading = {};
            this._cache = new Map();
            opts = this.opts = { ...opts, ...requiredOptions(opts) };
            const { es5, lines } = this.opts.code;
            this.scope = new codegen_2.ValueScope({ scope: {}, prefixes: EXT_SCOPE_NAMES, es5, lines });
            this.logger = getLogger(opts.logger);
            const formatOpt = opts.validateFormats;
            opts.validateFormats = false;
            this.RULES = (0, rules_1.getRules)();
            checkOptions.call(this, removedOptions, opts, 'NOT SUPPORTED');
            checkOptions.call(this, deprecatedOptions, opts, 'DEPRECATED', 'warn');
            this._metaOpts = getMetaSchemaOptions.call(this);
            if (opts.formats) addInitialFormats.call(this);
            this._addVocabularies();
            this._addDefaultMetaSchema();
            if (opts.keywords) addInitialKeywords.call(this, opts.keywords);
            if (typeof opts.meta === 'object') this.addMetaSchema(opts.meta);
            addInitialSchemas.call(this);
            opts.validateFormats = formatOpt;
          }
          _addVocabularies() {
            this.addKeyword('$async');
          }
          _addDefaultMetaSchema() {
            const { $data, meta, schemaId } = this.opts;
            let _dataRefSchema = $dataRefSchema;
            if (schemaId === 'id') {
              _dataRefSchema = { ...$dataRefSchema };
              _dataRefSchema.id = _dataRefSchema.$id;
              delete _dataRefSchema.$id;
            }
            if (meta && $data) this.addMetaSchema(_dataRefSchema, _dataRefSchema[schemaId], false);
          }
          defaultMeta() {
            const { meta, schemaId } = this.opts;
            return (this.opts.defaultMeta = typeof meta === 'object' ? meta[schemaId] || meta : undefined);
          }
          validate(
            schemaKeyRef, // key, ref or schema object
            data, // to be validated
          ) {
            let v;
            if (typeof schemaKeyRef === 'string') {
              v = this.getSchema(schemaKeyRef);
              if (!v) throw new Error(`no schema with key or ref "${schemaKeyRef}"`);
            } else {
              v = this.compile(schemaKeyRef);
            }
            const valid = v(data);
            if (!('$async' in v)) this.errors = v.errors;
            return valid;
          }
          compile(schema, _meta) {
            const sch = this._addSchema(schema, _meta);
            return (sch.validate || this._compileSchemaEnv(sch));
          }
          compileAsync(schema, meta) {
            if (typeof this.opts.loadSchema !== 'function') {
              throw new Error('options.loadSchema should be a function');
            }
            const { loadSchema } = this.opts;
            return runCompileAsync.call(this, schema, meta);
            async function runCompileAsync(_schema, _meta) {
              await loadMetaSchema.call(this, _schema.$schema);
              const sch = this._addSchema(_schema, _meta);
              return sch.validate || _compileAsync.call(this, sch);
            }
            async function loadMetaSchema($ref) {
              if ($ref && !this.getSchema($ref)) {
                await runCompileAsync.call(this, { $ref }, true);
              }
            }
            async function _compileAsync(sch) {
              try {
                return this._compileSchemaEnv(sch);
              } catch (e) {
                if (!(e instanceof ref_error_1.default)) throw e;
                checkLoaded.call(this, e);
                await loadMissingSchema.call(this, e.missingSchema);
                return _compileAsync.call(this, sch);
              }
            }
            function checkLoaded({ missingSchema: ref, missingRef }) {
              if (this.refs[ref]) {
                throw new Error(`AnySchema ${ref} is loaded but ${missingRef} cannot be resolved`);
              }
            }
            async function loadMissingSchema(ref) {
              const _schema = await _loadSchema.call(this, ref);
              if (!this.refs[ref]) await loadMetaSchema.call(this, _schema.$schema);
              if (!this.refs[ref]) this.addSchema(_schema, ref, meta);
            }
            async function _loadSchema(ref) {
              const p = this._loading[ref];
              if (p) return p;
              try {
                return await (this._loading[ref] = loadSchema(ref));
              } finally {
                delete this._loading[ref];
              }
            }
          }
          // Adds schema to the instance
          addSchema(
            schema, // If array is passed, `key` will be ignored
            key, // Optional schema key. Can be passed to `validate` method instead of schema object or id/ref. One schema per instance can have empty `id` and `key`.
            _meta, // true if schema is a meta-schema. Used internally, addMetaSchema should be used instead.
            _validateSchema = this.opts.validateSchema, // false to skip schema validation. Used internally, option validateSchema should be used instead.
          ) {
            if (Array.isArray(schema)) {
              for (const sch of schema) this.addSchema(sch, undefined, _meta, _validateSchema);
              return this;
            }
            let id;
            if (typeof schema === 'object') {
              const { schemaId } = this.opts;
              id = schema[schemaId];
              if (id !== undefined && typeof id !== 'string') {
                throw new Error(`schema ${schemaId} must be string`);
              }
            }
            key = (0, resolve_1.normalizeId)(key || id);
            this._checkUnique(key);
            this.schemas[key] = this._addSchema(schema, _meta, key, _validateSchema, true);
            return this;
          }
          // Add schema that will be used to validate other schemas
          // options in META_IGNORE_OPTIONS are alway set to false
          addMetaSchema(
            schema, key, // schema key
            _validateSchema = this.opts.validateSchema, // false to skip schema validation, can be used to override validateSchema option for meta-schema
          ) {
            this.addSchema(schema, key, true, _validateSchema);
            return this;
          }
          //  Validate schema against its meta-schema
          validateSchema(schema, throwOrLogError) {
            if (typeof schema === 'boolean') return true;
            let $schema;
            $schema = schema.$schema;
            if ($schema !== undefined && typeof $schema !== 'string') {
              throw new Error('$schema must be a string');
            }
            $schema = $schema || this.opts.defaultMeta || this.defaultMeta();
            if (!$schema) {
              this.logger.warn('meta-schema not available');
              this.errors = null;
              return true;
            }
            const valid = this.validate($schema, schema);
            if (!valid && throwOrLogError) {
              const message = `schema is invalid: ${this.errorsText()}`;
              if (this.opts.validateSchema === 'log') this.logger.error(message);
              else throw new Error(message);
            }
            return valid;
          }
          // Get compiled schema by `key` or `ref`.
          // (`key` that was passed to `addSchema` or full schema reference - `schema.$id` or resolved id)
          getSchema(keyRef) {
            let sch;
            while (typeof (sch = getSchEnv.call(this, keyRef)) === 'string') keyRef = sch;
            if (sch === undefined) {
              const { schemaId } = this.opts;
              const root = new compile_1.SchemaEnv({ schema: {}, schemaId });
              sch = compile_1.resolveSchema.call(this, root, keyRef);
              if (!sch) return;
              this.refs[keyRef] = sch;
            }
            return (sch.validate || this._compileSchemaEnv(sch));
          }
          // Remove cached schema(s).
          // If no parameter is passed all schemas but meta-schemas are removed.
          // If RegExp is passed all schemas with key/id matching pattern but meta-schemas are removed.
          // Even if schema is referenced by other schemas it still can be removed as other schemas have local references.
          removeSchema(schemaKeyRef) {
            if (schemaKeyRef instanceof RegExp) {
              this._removeAllSchemas(this.schemas, schemaKeyRef);
              this._removeAllSchemas(this.refs, schemaKeyRef);
              return this;
            }
            switch (typeof schemaKeyRef) {
              case 'undefined':
                this._removeAllSchemas(this.schemas);
                this._removeAllSchemas(this.refs);
                this._cache.clear();
                return this;
              case 'string': {
                const sch = getSchEnv.call(this, schemaKeyRef);
                if (typeof sch === 'object') this._cache.delete(sch.schema);
                delete this.schemas[schemaKeyRef];
                delete this.refs[schemaKeyRef];
                return this;
              }
              case 'object': {
                const cacheKey = schemaKeyRef;
                this._cache.delete(cacheKey);
                let id = schemaKeyRef[this.opts.schemaId];
                if (id) {
                  id = (0, resolve_1.normalizeId)(id);
                  delete this.schemas[id];
                  delete this.refs[id];
                }
                return this;
              }
              default:
                throw new Error('ajv.removeSchema: invalid parameter');
            }
          }
          // add "vocabulary" - a collection of keywords
          addVocabulary(definitions) {
            for (const def of definitions) this.addKeyword(def);
            return this;
          }
          addKeyword(kwdOrDef, def, // deprecated
          ) {
            let keyword;
            if (typeof kwdOrDef === 'string') {
              keyword = kwdOrDef;
              if (typeof def === 'object') {
                this.logger.warn('these parameters are deprecated, see docs for addKeyword');
                def.keyword = keyword;
              }
            } else if (typeof kwdOrDef === 'object' && def === undefined) {
              def = kwdOrDef;
              keyword = def.keyword;
              if (Array.isArray(keyword) && !keyword.length) {
                throw new Error('addKeywords: keyword must be string or non-empty array');
              }
            } else {
              throw new Error('invalid addKeywords parameters');
            }
            checkKeyword.call(this, keyword, def);
            if (!def) {
              (0, util_1.eachItem)(keyword, kwd => addRule.call(this, kwd));
              return this;
            }
            keywordMetaschema.call(this, def);
            const definition = {
              ...def,
              type: (0, dataType_1.getJSONTypes)(def.type),
              schemaType: (0, dataType_1.getJSONTypes)(def.schemaType),
            };
            (0, util_1.eachItem)(keyword, definition.type.length === 0
              ? k => addRule.call(this, k, definition)
              : k => definition.type.forEach(t => addRule.call(this, k, definition, t)));
            return this;
          }
          getKeyword(keyword) {
            const rule = this.RULES.all[keyword];
            return typeof rule === 'object' ? rule.definition : !!rule;
          }
          // Remove keyword
          removeKeyword(keyword) {
            // TODO return type should be Ajv
            const { RULES } = this;
            delete RULES.keywords[keyword];
            delete RULES.all[keyword];
            for (const group of RULES.rules) {
              const i = group.rules.findIndex(rule => rule.keyword === keyword);
              if (i >= 0) group.rules.splice(i, 1);
            }
            return this;
          }
          // Add format
          addFormat(name, format) {
            if (typeof format === 'string') format = new RegExp(format);
            this.formats[name] = format;
            return this;
          }
          errorsText(
            errors = this.errors, // optional array of validation errors
            { separator = ', ', dataVar = 'data' } = {}, // optional options with properties `separator` and `dataVar`
          ) {
            if (!errors || errors.length === 0) return 'No errors';
            return errors
              .map(e => `${dataVar}${e.instancePath} ${e.message}`)
              .reduce((text, msg) => text + separator + msg);
          }
          $dataMetaSchema(metaSchema, keywordsJsonPointers) {
            const rules = this.RULES.all;
            metaSchema = JSON.parse(JSON.stringify(metaSchema));
            for (const jsonPointer of keywordsJsonPointers) {
              const segments = jsonPointer.split('/').slice(1); // first segment is an empty string
              let keywords = metaSchema;
              for (const seg of segments) keywords = keywords[seg];
              for (const key in rules) {
                const rule = rules[key];
                if (typeof rule !== 'object') continue;
                const { $data } = rule.definition;
                const schema = keywords[key];
                if ($data && schema) keywords[key] = schemaOrData(schema);
              }
            }
            return metaSchema;
          }
          _removeAllSchemas(schemas, regex) {
            for (const keyRef in schemas) {
              const sch = schemas[keyRef];
              if (!regex || regex.test(keyRef)) {
                if (typeof sch === 'string') {
                  delete schemas[keyRef];
                } else if (sch && !sch.meta) {
                  this._cache.delete(sch.schema);
                  delete schemas[keyRef];
                }
              }
            }
          }
          _addSchema(schema, meta, baseId, validateSchema = this.opts.validateSchema, addSchema = this.opts.addUsedSchema) {
            let id;
            const { schemaId } = this.opts;
            if (typeof schema === 'object') {
              id = schema[schemaId];
            } else {
              if (this.opts.jtd) throw new Error('schema must be object');
              else if (typeof schema !== 'boolean') throw new Error('schema must be object or boolean');
            }
            let sch = this._cache.get(schema);
            if (sch !== undefined) return sch;
            baseId = (0, resolve_1.normalizeId)(id || baseId);
            const localRefs = resolve_1.getSchemaRefs.call(this, schema, baseId);
            sch = new compile_1.SchemaEnv({ schema, schemaId, meta, baseId, localRefs });
            this._cache.set(sch.schema, sch);
            if (addSchema && !baseId.startsWith('#')) {
            // TODO atm it is allowed to overwrite schemas without id (instead of not adding them)
              if (baseId) this._checkUnique(baseId);
              this.refs[baseId] = sch;
            }
            if (validateSchema) this.validateSchema(schema, true);
            return sch;
          }
          _checkUnique(id) {
            if (this.schemas[id] || this.refs[id]) {
              throw new Error(`schema with key or id "${id}" already exists`);
            }
          }
          _compileSchemaEnv(sch) {
            if (sch.meta) this._compileMetaSchema(sch);
            else compile_1.compileSchema.call(this, sch);
            /* istanbul ignore if */
            if (!sch.validate) throw new Error('ajv implementation error');
            return sch.validate;
          }
          _compileMetaSchema(sch) {
            const currentOpts = this.opts;
            this.opts = this._metaOpts;
            try {
              compile_1.compileSchema.call(this, sch);
            } finally {
              this.opts = currentOpts;
            }
          }
        }
        exports.default = Ajv;
        Ajv.ValidationError = validation_error_1.default;
        Ajv.MissingRefError = ref_error_1.default;
        function checkOptions(checkOpts, options, msg, log = 'error') {
          for (const key in checkOpts) {
            const opt = key;
            if (opt in options) this.logger[log](`${msg}: option ${key}. ${checkOpts[opt]}`);
          }
        }
        function getSchEnv(keyRef) {
          keyRef = (0, resolve_1.normalizeId)(keyRef); // TODO tests fail without this line
          return this.schemas[keyRef] || this.refs[keyRef];
        }
        function addInitialSchemas() {
          const optsSchemas = this.opts.schemas;
          if (!optsSchemas) return;
          if (Array.isArray(optsSchemas)) this.addSchema(optsSchemas);
          else for (const key in optsSchemas) this.addSchema(optsSchemas[key], key);
        }
        function addInitialFormats() {
          for (const name in this.opts.formats) {
            const format = this.opts.formats[name];
            if (format) this.addFormat(name, format);
          }
        }
        function addInitialKeywords(defs) {
          if (Array.isArray(defs)) {
            this.addVocabulary(defs);
            return;
          }
          this.logger.warn('keywords option as map is deprecated, pass array');
          for (const keyword in defs) {
            const def = defs[keyword];
            if (!def.keyword) def.keyword = keyword;
            this.addKeyword(def);
          }
        }
        function getMetaSchemaOptions() {
          const metaOpts = { ...this.opts };
          for (const opt of META_IGNORE_OPTIONS) delete metaOpts[opt];
          return metaOpts;
        }
        const noLogs = { log() { }, warn() { }, error() { } };
        function getLogger(logger) {
          if (logger === false) return noLogs;
          if (logger === undefined) return console;
          if (logger.log && logger.warn && logger.error) return logger;
          throw new Error('logger must implement log, warn and error methods');
        }
        const KEYWORD_NAME = /^[a-z_$][a-z0-9_$:-]*$/i;
        function checkKeyword(keyword, def) {
          const { RULES } = this;
          (0, util_1.eachItem)(keyword, (kwd) => {
            if (RULES.keywords[kwd]) throw new Error(`Keyword ${kwd} is already defined`);
            if (!KEYWORD_NAME.test(kwd)) throw new Error(`Keyword ${kwd} has invalid name`);
          });
          if (!def) return;
          if (def.$data && !('code' in def || 'validate' in def)) {
            throw new Error('$data keyword must have "code" or "validate" function');
          }
        }
        function addRule(keyword, definition, dataType) {
          let _a;
          const post = definition === null || definition === void 0 ? void 0 : definition.post;
          if (dataType && post) throw new Error('keyword with "post" flag cannot have "type"');
          const { RULES } = this;
          let ruleGroup = post ? RULES.post : RULES.rules.find(({ type: t }) => t === dataType);
          if (!ruleGroup) {
            ruleGroup = { type: dataType, rules: [] };
            RULES.rules.push(ruleGroup);
          }
          RULES.keywords[keyword] = true;
          if (!definition) return;
          const rule = {
            keyword,
            definition: {
              ...definition,
              type: (0, dataType_1.getJSONTypes)(definition.type),
              schemaType: (0, dataType_1.getJSONTypes)(definition.schemaType),
            },
          };
          if (definition.before) addBeforeRule.call(this, ruleGroup, rule, definition.before);
          else ruleGroup.rules.push(rule);
          RULES.all[keyword] = rule;
          (_a = definition.implements) === null || _a === void 0 ? void 0 : _a.forEach(kwd => this.addKeyword(kwd));
        }
        function addBeforeRule(ruleGroup, rule, before) {
          const i = ruleGroup.rules.findIndex(_rule => _rule.keyword === before);
          if (i >= 0) {
            ruleGroup.rules.splice(i, 0, rule);
          } else {
            ruleGroup.rules.push(rule);
            this.logger.warn(`rule ${before} is not defined`);
          }
        }
        function keywordMetaschema(def) {
          let { metaSchema } = def;
          if (metaSchema === undefined) return;
          if (def.$data && this.opts.$data) metaSchema = schemaOrData(metaSchema);
          def.validateSchema = this.compile(metaSchema, true);
        }
        const $dataRef = {
          $ref: 'https://raw.githubusercontent.com/ajv-validator/ajv/master/lib/refs/data.json#',
        };
        function schemaOrData(schema) {
          return { anyOf: [schema, $dataRef] };
        }
        // # sourceMappingURL=core.js.map
        /***/ }),

      /***/ 3510:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        // https://github.com/ajv-validator/ajv/issues/889
        const equal = __webpack_require__(4063);
        equal.code = 'require("ajv/dist/runtime/equal").default';
        exports.default = equal;
        // # sourceMappingURL=equal.js.map
        /***/ }),

      /***/ 4499:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        // https://mathiasbynens.be/notes/javascript-encoding
        // https://github.com/bestiejs/punycode.js - punycode.ucs2.decode
        function ucs2length(str) {
          const len = str.length;
          let length = 0;
          let pos = 0;
          let value;
          while (pos < len) {
            length++;
            value = str.charCodeAt(pos++);
            if (value >= 0xd800 && value <= 0xdbff && pos < len) {
            // high surrogate, and there is a next character
              value = str.charCodeAt(pos);
              if ((value & 0xfc00) === 0xdc00) pos++; // low surrogate
            }
          }
          return length;
        }
        exports.default = ucs2length;
        ucs2length.code = 'require("ajv/dist/runtime/ucs2length").default';
        // # sourceMappingURL=ucs2length.js.map
        /***/ }),

      /***/ 3589:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const uri = __webpack_require__(540);
        uri.code = 'require("ajv/dist/runtime/uri").default';
        exports.default = uri;
        // # sourceMappingURL=uri.js.map
        /***/ }),

      /***/ 7426:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        class ValidationError extends Error {
          constructor(errors) {
            super('validation failed');
            this.errors = errors;
            this.ajv = this.validation = true;
          }
        }
        exports.default = ValidationError;
        // # sourceMappingURL=validation_error.js.map
        /***/ }),

      /***/ 4783:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.validateAdditionalItems = void 0;
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const error = {
          message: ({ params: { len } }) => (0, codegen_1.str) `must NOT have more than ${len} items`,
          params: ({ params: { len } }) => (0, codegen_1._) `{limit: ${len}}`,
        };
        const def = {
          keyword: 'additionalItems',
          type: 'array',
          schemaType: ['boolean', 'object'],
          before: 'uniqueItems',
          error,
          code(cxt) {
            const { parentSchema, it } = cxt;
            const { items } = parentSchema;
            if (!Array.isArray(items)) {
              (0, util_1.checkStrictMode)(it, '"additionalItems" is ignored when "items" is not an array of schemas');
              return;
            }
            validateAdditionalItems(cxt, items);
          },
        };
        function validateAdditionalItems(cxt, items) {
          const { gen, schema, data, keyword, it } = cxt;
          it.items = true;
          const len = gen.const('len', (0, codegen_1._) `${data}.length`);
          if (schema === false) {
            cxt.setParams({ len: items.length });
            cxt.pass((0, codegen_1._) `${len} <= ${items.length}`);
          } else if (typeof schema === 'object' && !(0, util_1.alwaysValidSchema)(it, schema)) {
            const valid = gen.var('valid', (0, codegen_1._) `${len} <= ${items.length}`); // TODO var
            gen.if((0, codegen_1.not)(valid), () => validateItems(valid));
            cxt.ok(valid);
          }
          function validateItems(valid) {
            gen.forRange('i', items.length, len, (i) => {
              cxt.subschema({ keyword, dataProp: i, dataPropType: util_1.Type.Num }, valid);
              if (!it.allErrors) gen.if((0, codegen_1.not)(valid), () => gen.break());
            });
          }
        }
        exports.validateAdditionalItems = validateAdditionalItems;
        exports.default = def;
        // # sourceMappingURL=additionalItems.js.map
        /***/ }),

      /***/ 9351:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const code_1 = __webpack_require__(412);
        const codegen_1 = __webpack_require__(3487);
        const names_1 = __webpack_require__(2141);
        const util_1 = __webpack_require__(6776);
        const error = {
          message: 'must NOT have additional properties',
          params: ({ params }) => (0, codegen_1._) `{additionalProperty: ${params.additionalProperty}}`,
        };
        const def = {
          keyword: 'additionalProperties',
          type: ['object'],
          schemaType: ['boolean', 'object'],
          allowUndefined: true,
          trackErrors: true,
          error,
          code(cxt) {
            const { gen, schema, parentSchema, data, errsCount, it } = cxt;
            /* istanbul ignore if */
            if (!errsCount) throw new Error('ajv implementation error');
            const { allErrors, opts } = it;
            it.props = true;
            if (opts.removeAdditional !== 'all' && (0, util_1.alwaysValidSchema)(it, schema)) return;
            const props = (0, code_1.allSchemaProperties)(parentSchema.properties);
            const patProps = (0, code_1.allSchemaProperties)(parentSchema.patternProperties);
            checkAdditionalProperties();
            cxt.ok((0, codegen_1._) `${errsCount} === ${names_1.default.errors}`);
            function checkAdditionalProperties() {
              gen.forIn('key', data, (key) => {
                if (!props.length && !patProps.length) additionalPropertyCode(key);
                else gen.if(isAdditional(key), () => additionalPropertyCode(key));
              });
            }
            function isAdditional(key) {
              let definedProp;
              if (props.length > 8) {
                // TODO maybe an option instead of hard-coded 8?
                const propsSchema = (0, util_1.schemaRefOrVal)(it, parentSchema.properties, 'properties');
                definedProp = (0, code_1.isOwnProperty)(gen, propsSchema, key);
              } else if (props.length) {
                definedProp = (0, codegen_1.or)(...props.map(p => (0, codegen_1._) `${key} === ${p}`));
              } else {
                definedProp = codegen_1.nil;
              }
              if (patProps.length) {
                definedProp = (0, codegen_1.or)(definedProp, ...patProps.map(p => (0, codegen_1._) `${(0, code_1.usePattern)(cxt, p)}.test(${key})`));
              }
              return (0, codegen_1.not)(definedProp);
            }
            function deleteAdditional(key) {
              gen.code((0, codegen_1._) `delete ${data}[${key}]`);
            }
            function additionalPropertyCode(key) {
              if (opts.removeAdditional === 'all' || (opts.removeAdditional && schema === false)) {
                deleteAdditional(key);
                return;
              }
              if (schema === false) {
                cxt.setParams({ additionalProperty: key });
                cxt.error();
                if (!allErrors) gen.break();
                return;
              }
              if (typeof schema === 'object' && !(0, util_1.alwaysValidSchema)(it, schema)) {
                const valid = gen.name('valid');
                if (opts.removeAdditional === 'failing') {
                  applyAdditionalSchema(key, valid, false);
                  gen.if((0, codegen_1.not)(valid), () => {
                    cxt.reset();
                    deleteAdditional(key);
                  });
                } else {
                  applyAdditionalSchema(key, valid);
                  if (!allErrors) gen.if((0, codegen_1.not)(valid), () => gen.break());
                }
              }
            }
            function applyAdditionalSchema(key, valid, errors) {
              const subschema = {
                keyword: 'additionalProperties',
                dataProp: key,
                dataPropType: util_1.Type.Str,
              };
              if (errors === false) {
                Object.assign(subschema, {
                  compositeRule: true,
                  createErrors: false,
                  allErrors: false,
                });
              }
              cxt.subschema(subschema, valid);
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=additionalProperties.js.map
        /***/ }),

      /***/ 1125:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const util_1 = __webpack_require__(6776);
        const def = {
          keyword: 'allOf',
          schemaType: 'array',
          code(cxt) {
            const { gen, schema, it } = cxt;
            /* istanbul ignore if */
            if (!Array.isArray(schema)) throw new Error('ajv implementation error');
            const valid = gen.name('valid');
            schema.forEach((sch, i) => {
              if ((0, util_1.alwaysValidSchema)(it, sch)) return;
              const schCxt = cxt.subschema({ keyword: 'allOf', schemaProp: i }, valid);
              cxt.ok(valid);
              cxt.mergeEvaluated(schCxt);
            });
          },
        };
        exports.default = def;
        // # sourceMappingURL=allOf.js.map
        /***/ }),

      /***/ 19:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const code_1 = __webpack_require__(412);
        const def = {
          keyword: 'anyOf',
          schemaType: 'array',
          trackErrors: true,
          code: code_1.validateUnion,
          error: { message: 'must match a schema in anyOf' },
        };
        exports.default = def;
        // # sourceMappingURL=anyOf.js.map
        /***/ }),

      /***/ 9864:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const error = {
          message: ({ params: { min, max } }) => (max === undefined
            ? (0, codegen_1.str) `must contain at least ${min} valid item(s)`
            : (0, codegen_1.str) `must contain at least ${min} and no more than ${max} valid item(s)`),
          params: ({ params: { min, max } }) => (max === undefined ? (0, codegen_1._) `{minContains: ${min}}` : (0, codegen_1._) `{minContains: ${min}, maxContains: ${max}}`),
        };
        const def = {
          keyword: 'contains',
          type: 'array',
          schemaType: ['object', 'boolean'],
          before: 'uniqueItems',
          trackErrors: true,
          error,
          code(cxt) {
            const { gen, schema, parentSchema, data, it } = cxt;
            let min;
            let max;
            const { minContains, maxContains } = parentSchema;
            if (it.opts.next) {
              min = minContains === undefined ? 1 : minContains;
              max = maxContains;
            } else {
              min = 1;
            }
            const len = gen.const('len', (0, codegen_1._) `${data}.length`);
            cxt.setParams({ min, max });
            if (max === undefined && min === 0) {
              (0, util_1.checkStrictMode)(it, '"minContains" == 0 without "maxContains": "contains" keyword ignored');
              return;
            }
            if (max !== undefined && min > max) {
              (0, util_1.checkStrictMode)(it, '"minContains" > "maxContains" is always invalid');
              cxt.fail();
              return;
            }
            if ((0, util_1.alwaysValidSchema)(it, schema)) {
              let cond = (0, codegen_1._) `${len} >= ${min}`;
              if (max !== undefined) cond = (0, codegen_1._) `${cond} && ${len} <= ${max}`;
              cxt.pass(cond);
              return;
            }
            it.items = true;
            const valid = gen.name('valid');
            if (max === undefined && min === 1) {
              validateItems(valid, () => gen.if(valid, () => gen.break()));
            } else if (min === 0) {
              gen.let(valid, true);
              if (max !== undefined) gen.if((0, codegen_1._) `${data}.length > 0`, validateItemsWithCount);
            } else {
              gen.let(valid, false);
              validateItemsWithCount();
            }
            cxt.result(valid, () => cxt.reset());
            function validateItemsWithCount() {
              const schValid = gen.name('_valid');
              const count = gen.let('count', 0);
              validateItems(schValid, () => gen.if(schValid, () => checkLimits(count)));
            }
            function validateItems(_valid, block) {
              gen.forRange('i', 0, len, (i) => {
                cxt.subschema({
                  keyword: 'contains',
                  dataProp: i,
                  dataPropType: util_1.Type.Num,
                  compositeRule: true,
                }, _valid);
                block();
              });
            }
            function checkLimits(count) {
              gen.code((0, codegen_1._) `${count}++`);
              if (max === undefined) {
                gen.if((0, codegen_1._) `${count} >= ${min}`, () => gen.assign(valid, true).break());
              } else {
                gen.if((0, codegen_1._) `${count} > ${max}`, () => gen.assign(valid, false).break());
                if (min === 1) gen.assign(valid, true);
                else gen.if((0, codegen_1._) `${count} >= ${min}`, () => gen.assign(valid, true));
              }
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=contains.js.map
        /***/ }),

      /***/ 7772:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.validateSchemaDeps = exports.validatePropertyDeps = exports.error = void 0;
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const code_1 = __webpack_require__(412);
        exports.error = {
          message: ({ params: { property, depsCount, deps } }) => {
            const property_ies = depsCount === 1 ? 'property' : 'properties';
            return (0, codegen_1.str) `must have ${property_ies} ${deps} when property ${property} is present`;
          },
          params: ({ params: { property, depsCount, deps, missingProperty } }) => (0, codegen_1._) `{property: ${property},
    missingProperty: ${missingProperty},
    depsCount: ${depsCount},
    deps: ${deps}}`, // TODO change to reference
        };
        const def = {
          keyword: 'dependencies',
          type: 'object',
          schemaType: 'object',
          error: exports.error,
          code(cxt) {
            const [propDeps, schDeps] = splitDependencies(cxt);
            validatePropertyDeps(cxt, propDeps);
            validateSchemaDeps(cxt, schDeps);
          },
        };
        function splitDependencies({ schema }) {
          const propertyDeps = {};
          const schemaDeps = {};
          for (const key in schema) {
            if (key === '__proto__') continue;
            const deps = Array.isArray(schema[key]) ? propertyDeps : schemaDeps;
            deps[key] = schema[key];
          }
          return [propertyDeps, schemaDeps];
        }
        function validatePropertyDeps(cxt, propertyDeps = cxt.schema) {
          const { gen, data, it } = cxt;
          if (Object.keys(propertyDeps).length === 0) return;
          const missing = gen.let('missing');
          for (const prop in propertyDeps) {
            const deps = propertyDeps[prop];
            if (deps.length === 0) continue;
            const hasProperty = (0, code_1.propertyInData)(gen, data, prop, it.opts.ownProperties);
            cxt.setParams({
              property: prop,
              depsCount: deps.length,
              deps: deps.join(', '),
            });
            if (it.allErrors) {
              gen.if(hasProperty, () => {
                for (const depProp of deps) {
                  (0, code_1.checkReportMissingProp)(cxt, depProp);
                }
              });
            } else {
              gen.if((0, codegen_1._) `${hasProperty} && (${(0, code_1.checkMissingProp)(cxt, deps, missing)})`);
              (0, code_1.reportMissingProp)(cxt, missing);
              gen.else();
            }
          }
        }
        exports.validatePropertyDeps = validatePropertyDeps;
        function validateSchemaDeps(cxt, schemaDeps = cxt.schema) {
          const { gen, data, keyword, it } = cxt;
          const valid = gen.name('valid');
          for (const prop in schemaDeps) {
            if ((0, util_1.alwaysValidSchema)(it, schemaDeps[prop])) continue;
            gen.if((0, code_1.propertyInData)(gen, data, prop, it.opts.ownProperties), () => {
              const schCxt = cxt.subschema({ keyword, schemaProp: prop }, valid);
              cxt.mergeValidEvaluated(schCxt, valid);
            }, () => gen.var(valid, true), // TODO var
            );
            cxt.ok(valid);
          }
        }
        exports.validateSchemaDeps = validateSchemaDeps;
        exports.default = def;
        // # sourceMappingURL=dependencies.js.map
        /***/ }),

      /***/ 1531:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const error = {
          message: ({ params }) => (0, codegen_1.str) `must match "${params.ifClause}" schema`,
          params: ({ params }) => (0, codegen_1._) `{failingKeyword: ${params.ifClause}}`,
        };
        const def = {
          keyword: 'if',
          schemaType: ['object', 'boolean'],
          trackErrors: true,
          error,
          code(cxt) {
            const { gen, parentSchema, it } = cxt;
            if (parentSchema.then === undefined && parentSchema.else === undefined) {
              (0, util_1.checkStrictMode)(it, '"if" without "then" and "else" is ignored');
            }
            const hasThen = hasSchema(it, 'then');
            const hasElse = hasSchema(it, 'else');
            if (!hasThen && !hasElse) return;
            const valid = gen.let('valid', true);
            const schValid = gen.name('_valid');
            validateIf();
            cxt.reset();
            if (hasThen && hasElse) {
              const ifClause = gen.let('ifClause');
              cxt.setParams({ ifClause });
              gen.if(schValid, validateClause('then', ifClause), validateClause('else', ifClause));
            } else if (hasThen) {
              gen.if(schValid, validateClause('then'));
            } else {
              gen.if((0, codegen_1.not)(schValid), validateClause('else'));
            }
            cxt.pass(valid, () => cxt.error(true));
            function validateIf() {
              const schCxt = cxt.subschema({
                keyword: 'if',
                compositeRule: true,
                createErrors: false,
                allErrors: false,
              }, schValid);
              cxt.mergeEvaluated(schCxt);
            }
            function validateClause(keyword, ifClause) {
              return () => {
                const schCxt = cxt.subschema({ keyword }, schValid);
                gen.assign(valid, schValid);
                cxt.mergeValidEvaluated(schCxt, valid);
                if (ifClause) gen.assign(ifClause, (0, codegen_1._) `${keyword}`);
                else cxt.setParams({ ifClause: keyword });
              };
            }
          },
        };
        function hasSchema(it, keyword) {
          const schema = it.schema[keyword];
          return schema !== undefined && !(0, util_1.alwaysValidSchema)(it, schema);
        }
        exports.default = def;
        // # sourceMappingURL=if.js.map
        /***/ }),

      /***/ 8200:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const additionalItems_1 = __webpack_require__(4783);
        const prefixItems_1 = __webpack_require__(2924);
        const items_1 = __webpack_require__(4665);
        const items2020_1 = __webpack_require__(1119);
        const contains_1 = __webpack_require__(9864);
        const dependencies_1 = __webpack_require__(7772);
        const propertyNames_1 = __webpack_require__(3708);
        const additionalProperties_1 = __webpack_require__(9351);
        const properties_1 = __webpack_require__(6239);
        const patternProperties_1 = __webpack_require__(2296);
        const not_1 = __webpack_require__(5697);
        const anyOf_1 = __webpack_require__(19);
        const oneOf_1 = __webpack_require__(4200);
        const allOf_1 = __webpack_require__(1125);
        const if_1 = __webpack_require__(1531);
        const thenElse_1 = __webpack_require__(6552);
        function getApplicator(draft2020 = false) {
          const applicator = [
            // any
            not_1.default,
            anyOf_1.default,
            oneOf_1.default,
            allOf_1.default,
            if_1.default,
            thenElse_1.default,
            // object
            propertyNames_1.default,
            additionalProperties_1.default,
            dependencies_1.default,
            properties_1.default,
            patternProperties_1.default,
          ];
          // array
          if (draft2020) applicator.push(prefixItems_1.default, items2020_1.default);
          else applicator.push(additionalItems_1.default, items_1.default);
          applicator.push(contains_1.default);
          return applicator;
        }
        exports.default = getApplicator;
        // # sourceMappingURL=index.js.map
        /***/ }),

      /***/ 4665:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.validateTuple = void 0;
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const code_1 = __webpack_require__(412);
        const def = {
          keyword: 'items',
          type: 'array',
          schemaType: ['object', 'array', 'boolean'],
          before: 'uniqueItems',
          code(cxt) {
            const { schema, it } = cxt;
            if (Array.isArray(schema)) return validateTuple(cxt, 'additionalItems', schema);
            it.items = true;
            if ((0, util_1.alwaysValidSchema)(it, schema)) return;
            cxt.ok((0, code_1.validateArray)(cxt));
          },
        };
        function validateTuple(cxt, extraItems, schArr = cxt.schema) {
          const { gen, parentSchema, data, keyword, it } = cxt;
          checkStrictTuple(parentSchema);
          if (it.opts.unevaluated && schArr.length && it.items !== true) {
            it.items = util_1.mergeEvaluated.items(gen, schArr.length, it.items);
          }
          const valid = gen.name('valid');
          const len = gen.const('len', (0, codegen_1._) `${data}.length`);
          schArr.forEach((sch, i) => {
            if ((0, util_1.alwaysValidSchema)(it, sch)) return;
            gen.if((0, codegen_1._) `${len} > ${i}`, () => cxt.subschema({
              keyword,
              schemaProp: i,
              dataProp: i,
            }, valid));
            cxt.ok(valid);
          });
          function checkStrictTuple(sch) {
            const { opts, errSchemaPath } = it;
            const l = schArr.length;
            const fullTuple = l === sch.minItems && (l === sch.maxItems || sch[extraItems] === false);
            if (opts.strictTuples && !fullTuple) {
              const msg = `"${keyword}" is ${l}-tuple, but minItems or maxItems/${extraItems} are not specified or different at path "${errSchemaPath}"`;
              (0, util_1.checkStrictMode)(it, msg, opts.strictTuples);
            }
          }
        }
        exports.validateTuple = validateTuple;
        exports.default = def;
        // # sourceMappingURL=items.js.map
        /***/ }),

      /***/ 1119:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const code_1 = __webpack_require__(412);
        const additionalItems_1 = __webpack_require__(4783);
        const error = {
          message: ({ params: { len } }) => (0, codegen_1.str) `must NOT have more than ${len} items`,
          params: ({ params: { len } }) => (0, codegen_1._) `{limit: ${len}}`,
        };
        const def = {
          keyword: 'items',
          type: 'array',
          schemaType: ['object', 'boolean'],
          before: 'uniqueItems',
          error,
          code(cxt) {
            const { schema, parentSchema, it } = cxt;
            const { prefixItems } = parentSchema;
            it.items = true;
            if ((0, util_1.alwaysValidSchema)(it, schema)) return;
            if (prefixItems) (0, additionalItems_1.validateAdditionalItems)(cxt, prefixItems);
            else cxt.ok((0, code_1.validateArray)(cxt));
          },
        };
        exports.default = def;
        // # sourceMappingURL=items2020.js.map
        /***/ }),

      /***/ 5697:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const util_1 = __webpack_require__(6776);
        const def = {
          keyword: 'not',
          schemaType: ['object', 'boolean'],
          trackErrors: true,
          code(cxt) {
            const { gen, schema, it } = cxt;
            if ((0, util_1.alwaysValidSchema)(it, schema)) {
              cxt.fail();
              return;
            }
            const valid = gen.name('valid');
            cxt.subschema({
              keyword: 'not',
              compositeRule: true,
              createErrors: false,
              allErrors: false,
            }, valid);
            cxt.failResult(valid, () => cxt.reset(), () => cxt.error());
          },
          error: { message: 'must NOT be valid' },
        };
        exports.default = def;
        // # sourceMappingURL=not.js.map
        /***/ }),

      /***/ 4200:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const error = {
          message: 'must match exactly one schema in oneOf',
          params: ({ params }) => (0, codegen_1._) `{passingSchemas: ${params.passing}}`,
        };
        const def = {
          keyword: 'oneOf',
          schemaType: 'array',
          trackErrors: true,
          error,
          code(cxt) {
            const { gen, schema, parentSchema, it } = cxt;
            /* istanbul ignore if */
            if (!Array.isArray(schema)) throw new Error('ajv implementation error');
            if (it.opts.discriminator && parentSchema.discriminator) return;
            const schArr = schema;
            const valid = gen.let('valid', false);
            const passing = gen.let('passing', null);
            const schValid = gen.name('_valid');
            cxt.setParams({ passing });
            // TODO possibly fail straight away (with warning or exception) if there are two empty always valid schemas
            gen.block(validateOneOf);
            cxt.result(valid, () => cxt.reset(), () => cxt.error(true));
            function validateOneOf() {
              schArr.forEach((sch, i) => {
                let schCxt;
                if ((0, util_1.alwaysValidSchema)(it, sch)) {
                  gen.var(schValid, true);
                } else {
                  schCxt = cxt.subschema({
                    keyword: 'oneOf',
                    schemaProp: i,
                    compositeRule: true,
                  }, schValid);
                }
                if (i > 0) {
                  gen
                    .if((0, codegen_1._) `${schValid} && ${valid}`)
                    .assign(valid, false)
                    .assign(passing, (0, codegen_1._) `[${passing}, ${i}]`)
                    .else();
                }
                gen.if(schValid, () => {
                  gen.assign(valid, true);
                  gen.assign(passing, i);
                  if (schCxt) cxt.mergeEvaluated(schCxt, codegen_1.Name);
                });
              });
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=oneOf.js.map
        /***/ }),

      /***/ 2296:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const code_1 = __webpack_require__(412);
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const util_2 = __webpack_require__(6776);
        const def = {
          keyword: 'patternProperties',
          type: 'object',
          schemaType: 'object',
          code(cxt) {
            const { gen, schema, data, parentSchema, it } = cxt;
            const { opts } = it;
            const patterns = (0, code_1.allSchemaProperties)(schema);
            const alwaysValidPatterns = patterns.filter(p => (0, util_1.alwaysValidSchema)(it, schema[p]));
            if (patterns.length === 0
            || (alwaysValidPatterns.length === patterns.length
                && (!it.opts.unevaluated || it.props === true))) {
              return;
            }
            const checkProperties = opts.strictSchema && !opts.allowMatchingProperties && parentSchema.properties;
            const valid = gen.name('valid');
            if (it.props !== true && !(it.props instanceof codegen_1.Name)) {
              it.props = (0, util_2.evaluatedPropsToName)(gen, it.props);
            }
            const { props } = it;
            validatePatternProperties();
            function validatePatternProperties() {
              for (const pat of patterns) {
                if (checkProperties) checkMatchingProperties(pat);
                if (it.allErrors) {
                  validateProperties(pat);
                } else {
                  gen.var(valid, true); // TODO var
                  validateProperties(pat);
                  gen.if(valid);
                }
              }
            }
            function checkMatchingProperties(pat) {
              for (const prop in checkProperties) {
                if (new RegExp(pat).test(prop)) {
                  (0, util_1.checkStrictMode)(it, `property ${prop} matches pattern ${pat} (use allowMatchingProperties)`);
                }
              }
            }
            function validateProperties(pat) {
              gen.forIn('key', data, (key) => {
                gen.if((0, codegen_1._) `${(0, code_1.usePattern)(cxt, pat)}.test(${key})`, () => {
                  const alwaysValid = alwaysValidPatterns.includes(pat);
                  if (!alwaysValid) {
                    cxt.subschema({
                      keyword: 'patternProperties',
                      schemaProp: pat,
                      dataProp: key,
                      dataPropType: util_2.Type.Str,
                    }, valid);
                  }
                  if (it.opts.unevaluated && props !== true) {
                    gen.assign((0, codegen_1._) `${props}[${key}]`, true);
                  } else if (!alwaysValid && !it.allErrors) {
                    // can short-circuit if `unevaluatedProperties` is not supported (opts.next === false)
                    // or if all properties were evaluated (props === true)
                    gen.if((0, codegen_1.not)(valid), () => gen.break());
                  }
                });
              });
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=patternProperties.js.map
        /***/ }),

      /***/ 2924:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const items_1 = __webpack_require__(4665);
        const def = {
          keyword: 'prefixItems',
          type: 'array',
          schemaType: ['array'],
          before: 'uniqueItems',
          code: cxt => (0, items_1.validateTuple)(cxt, 'items'),
        };
        exports.default = def;
        // # sourceMappingURL=prefixItems.js.map
        /***/ }),

      /***/ 6239:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const validate_1 = __webpack_require__(4815);
        const code_1 = __webpack_require__(412);
        const util_1 = __webpack_require__(6776);
        const additionalProperties_1 = __webpack_require__(9351);
        const def = {
          keyword: 'properties',
          type: 'object',
          schemaType: 'object',
          code(cxt) {
            const { gen, schema, parentSchema, data, it } = cxt;
            if (it.opts.removeAdditional === 'all' && parentSchema.additionalProperties === undefined) {
              additionalProperties_1.default.code(new validate_1.KeywordCxt(it, additionalProperties_1.default, 'additionalProperties'));
            }
            const allProps = (0, code_1.allSchemaProperties)(schema);
            for (const prop of allProps) {
              it.definedProperties.add(prop);
            }
            if (it.opts.unevaluated && allProps.length && it.props !== true) {
              it.props = util_1.mergeEvaluated.props(gen, (0, util_1.toHash)(allProps), it.props);
            }
            const properties = allProps.filter(p => !(0, util_1.alwaysValidSchema)(it, schema[p]));
            if (properties.length === 0) return;
            const valid = gen.name('valid');
            for (const prop of properties) {
              if (hasDefault(prop)) {
                applyPropertySchema(prop);
              } else {
                gen.if((0, code_1.propertyInData)(gen, data, prop, it.opts.ownProperties));
                applyPropertySchema(prop);
                if (!it.allErrors) gen.else().var(valid, true);
                gen.endIf();
              }
              cxt.it.definedProperties.add(prop);
              cxt.ok(valid);
            }
            function hasDefault(prop) {
              return it.opts.useDefaults && !it.compositeRule && schema[prop].default !== undefined;
            }
            function applyPropertySchema(prop) {
              cxt.subschema({
                keyword: 'properties',
                schemaProp: prop,
                dataProp: prop,
              }, valid);
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=properties.js.map
        /***/ }),

      /***/ 3708:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const error = {
          message: 'property name must be valid',
          params: ({ params }) => (0, codegen_1._) `{propertyName: ${params.propertyName}}`,
        };
        const def = {
          keyword: 'propertyNames',
          type: 'object',
          schemaType: ['object', 'boolean'],
          error,
          code(cxt) {
            const { gen, schema, data, it } = cxt;
            if ((0, util_1.alwaysValidSchema)(it, schema)) return;
            const valid = gen.name('valid');
            gen.forIn('key', data, (key) => {
              cxt.setParams({ propertyName: key });
              cxt.subschema({
                keyword: 'propertyNames',
                data: key,
                dataTypes: ['string'],
                propertyName: key,
                compositeRule: true,
              }, valid);
              gen.if((0, codegen_1.not)(valid), () => {
                cxt.error(true);
                if (!it.allErrors) gen.break();
              });
            });
            cxt.ok(valid);
          },
        };
        exports.default = def;
        // # sourceMappingURL=propertyNames.js.map
        /***/ }),

      /***/ 6552:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const util_1 = __webpack_require__(6776);
        const def = {
          keyword: ['then', 'else'],
          schemaType: ['object', 'boolean'],
          code({ keyword, parentSchema, it }) {
            if (parentSchema.if === undefined) (0, util_1.checkStrictMode)(it, `"${keyword}" without "if" is ignored`);
          },
        };
        exports.default = def;
        // # sourceMappingURL=thenElse.js.map
        /***/ }),

      /***/ 412:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.validateUnion = exports.validateArray = exports.usePattern = exports.callValidateCode = exports.schemaProperties = exports.allSchemaProperties = exports.noPropertyInData = exports.propertyInData = exports.isOwnProperty = exports.hasPropFunc = exports.reportMissingProp = exports.checkMissingProp = exports.checkReportMissingProp = void 0;
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const names_1 = __webpack_require__(2141);
        const util_2 = __webpack_require__(6776);
        function checkReportMissingProp(cxt, prop) {
          const { gen, data, it } = cxt;
          gen.if(noPropertyInData(gen, data, prop, it.opts.ownProperties), () => {
            cxt.setParams({ missingProperty: (0, codegen_1._) `${prop}` }, true);
            cxt.error();
          });
        }
        exports.checkReportMissingProp = checkReportMissingProp;
        function checkMissingProp({ gen, data, it: { opts } }, properties, missing) {
          return (0, codegen_1.or)(...properties.map(prop => (0, codegen_1.and)(noPropertyInData(gen, data, prop, opts.ownProperties), (0, codegen_1._) `${missing} = ${prop}`)));
        }
        exports.checkMissingProp = checkMissingProp;
        function reportMissingProp(cxt, missing) {
          cxt.setParams({ missingProperty: missing }, true);
          cxt.error();
        }
        exports.reportMissingProp = reportMissingProp;
        function hasPropFunc(gen) {
          return gen.scopeValue('func', {
            // eslint-disable-next-line @typescript-eslint/unbound-method
            ref: Object.prototype.hasOwnProperty,
            code: (0, codegen_1._) `Object.prototype.hasOwnProperty`,
          });
        }
        exports.hasPropFunc = hasPropFunc;
        function isOwnProperty(gen, data, property) {
          return (0, codegen_1._) `${hasPropFunc(gen)}.call(${data}, ${property})`;
        }
        exports.isOwnProperty = isOwnProperty;
        function propertyInData(gen, data, property, ownProperties) {
          const cond = (0, codegen_1._) `${data}${(0, codegen_1.getProperty)(property)} !== undefined`;
          return ownProperties ? (0, codegen_1._) `${cond} && ${isOwnProperty(gen, data, property)}` : cond;
        }
        exports.propertyInData = propertyInData;
        function noPropertyInData(gen, data, property, ownProperties) {
          const cond = (0, codegen_1._) `${data}${(0, codegen_1.getProperty)(property)} === undefined`;
          return ownProperties ? (0, codegen_1.or)(cond, (0, codegen_1.not)(isOwnProperty(gen, data, property))) : cond;
        }
        exports.noPropertyInData = noPropertyInData;
        function allSchemaProperties(schemaMap) {
          return schemaMap ? Object.keys(schemaMap).filter(p => p !== '__proto__') : [];
        }
        exports.allSchemaProperties = allSchemaProperties;
        function schemaProperties(it, schemaMap) {
          return allSchemaProperties(schemaMap).filter(p => !(0, util_1.alwaysValidSchema)(it, schemaMap[p]));
        }
        exports.schemaProperties = schemaProperties;
        function callValidateCode({ schemaCode, data, it: { gen, topSchemaRef, schemaPath, errorPath }, it }, func, context, passSchema) {
          const dataAndSchema = passSchema ? (0, codegen_1._) `${schemaCode}, ${data}, ${topSchemaRef}${schemaPath}` : data;
          const valCxt = [
            [names_1.default.instancePath, (0, codegen_1.strConcat)(names_1.default.instancePath, errorPath)],
            [names_1.default.parentData, it.parentData],
            [names_1.default.parentDataProperty, it.parentDataProperty],
            [names_1.default.rootData, names_1.default.rootData],
          ];
          if (it.opts.dynamicRef) valCxt.push([names_1.default.dynamicAnchors, names_1.default.dynamicAnchors]);
          const args = (0, codegen_1._) `${dataAndSchema}, ${gen.object(...valCxt)}`;
          return context !== codegen_1.nil ? (0, codegen_1._) `${func}.call(${context}, ${args})` : (0, codegen_1._) `${func}(${args})`;
        }
        exports.callValidateCode = callValidateCode;
        const newRegExp = (0, codegen_1._) `new RegExp`;
        function usePattern({ gen, it: { opts } }, pattern) {
          const u = opts.unicodeRegExp ? 'u' : '';
          const { regExp } = opts.code;
          const rx = regExp(pattern, u);
          return gen.scopeValue('pattern', {
            key: rx.toString(),
            ref: rx,
            code: (0, codegen_1._) `${regExp.code === 'new RegExp' ? newRegExp : (0, util_2.useFunc)(gen, regExp)}(${pattern}, ${u})`,
          });
        }
        exports.usePattern = usePattern;
        function validateArray(cxt) {
          const { gen, data, keyword, it } = cxt;
          const valid = gen.name('valid');
          if (it.allErrors) {
            const validArr = gen.let('valid', true);
            validateItems(() => gen.assign(validArr, false));
            return validArr;
          }
          gen.var(valid, true);
          validateItems(() => gen.break());
          return valid;
          function validateItems(notValid) {
            const len = gen.const('len', (0, codegen_1._) `${data}.length`);
            gen.forRange('i', 0, len, (i) => {
              cxt.subschema({
                keyword,
                dataProp: i,
                dataPropType: util_1.Type.Num,
              }, valid);
              gen.if((0, codegen_1.not)(valid), notValid);
            });
          }
        }
        exports.validateArray = validateArray;
        function validateUnion(cxt) {
          const { gen, schema, keyword, it } = cxt;
          /* istanbul ignore if */
          if (!Array.isArray(schema)) throw new Error('ajv implementation error');
          const alwaysValid = schema.some(sch => (0, util_1.alwaysValidSchema)(it, sch));
          if (alwaysValid && !it.opts.unevaluated) return;
          const valid = gen.let('valid', false);
          const schValid = gen.name('_valid');
          gen.block(() => schema.forEach((_sch, i) => {
            const schCxt = cxt.subschema({
              keyword,
              schemaProp: i,
              compositeRule: true,
            }, schValid);
            gen.assign(valid, (0, codegen_1._) `${valid} || ${schValid}`);
            const merged = cxt.mergeValidEvaluated(schCxt, schValid);
            // can short-circuit if `unevaluatedProperties/Items` not supported (opts.unevaluated !== true)
            // or if all properties and items were evaluated (it.props === true && it.items === true)
            if (!merged) gen.if((0, codegen_1.not)(valid));
          }));
          cxt.result(valid, () => cxt.reset(), () => cxt.error(true));
        }
        exports.validateUnion = validateUnion;
        // # sourceMappingURL=code.js.map
        /***/ }),

      /***/ 8386:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const def = {
          keyword: 'id',
          code() {
            throw new Error('NOT SUPPORTED: keyword "id", use "$id" for schema ID');
          },
        };
        exports.default = def;
        // # sourceMappingURL=id.js.map
        /***/ }),

      /***/ 9283:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const id_1 = __webpack_require__(8386);
        const ref_1 = __webpack_require__(8280);
        const core = [
          '$schema',
          '$id',
          '$defs',
          '$vocabulary',
          { keyword: '$comment' },
          'definitions',
          id_1.default,
          ref_1.default,
        ];
        exports.default = core;
        // # sourceMappingURL=index.js.map
        /***/ }),

      /***/ 8280:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.callRef = exports.getValidate = void 0;
        const ref_error_1 = __webpack_require__(6646);
        const code_1 = __webpack_require__(412);
        const codegen_1 = __webpack_require__(3487);
        const names_1 = __webpack_require__(2141);
        const compile_1 = __webpack_require__(5173);
        const util_1 = __webpack_require__(6776);
        const def = {
          keyword: '$ref',
          schemaType: 'string',
          code(cxt) {
            const { gen, schema: $ref, it } = cxt;
            const { baseId, schemaEnv: env, validateName, opts, self } = it;
            const { root } = env;
            if (($ref === '#' || $ref === '#/') && baseId === root.baseId) return callRootRef();
            const schOrEnv = compile_1.resolveRef.call(self, root, baseId, $ref);
            if (schOrEnv === undefined) throw new ref_error_1.default(it.opts.uriResolver, baseId, $ref);
            if (schOrEnv instanceof compile_1.SchemaEnv) return callValidate(schOrEnv);
            return inlineRefSchema(schOrEnv);
            function callRootRef() {
              if (env === root) return callRef(cxt, validateName, env, env.$async);
              const rootName = gen.scopeValue('root', { ref: root });
              return callRef(cxt, (0, codegen_1._) `${rootName}.validate`, root, root.$async);
            }
            function callValidate(sch) {
              const v = getValidate(cxt, sch);
              callRef(cxt, v, sch, sch.$async);
            }
            function inlineRefSchema(sch) {
              const schName = gen.scopeValue('schema', opts.code.source === true ? { ref: sch, code: (0, codegen_1.stringify)(sch) } : { ref: sch });
              const valid = gen.name('valid');
              const schCxt = cxt.subschema({
                schema: sch,
                dataTypes: [],
                schemaPath: codegen_1.nil,
                topSchemaRef: schName,
                errSchemaPath: $ref,
              }, valid);
              cxt.mergeEvaluated(schCxt);
              cxt.ok(valid);
            }
          },
        };
        function getValidate(cxt, sch) {
          const { gen } = cxt;
          return sch.validate
            ? gen.scopeValue('validate', { ref: sch.validate })
            : (0, codegen_1._) `${gen.scopeValue('wrapper', { ref: sch })}.validate`;
        }
        exports.getValidate = getValidate;
        function callRef(cxt, v, sch, $async) {
          const { gen, it } = cxt;
          const { allErrors, schemaEnv: env, opts } = it;
          const passCxt = opts.passContext ? names_1.default.this : codegen_1.nil;
          if ($async) callAsyncRef();
          else callSyncRef();
          function callAsyncRef() {
            if (!env.$async) throw new Error('async schema referenced by sync schema');
            const valid = gen.let('valid');
            gen.try(() => {
              gen.code((0, codegen_1._) `await ${(0, code_1.callValidateCode)(cxt, v, passCxt)}`);
              addEvaluatedFrom(v); // TODO will not work with async, it has to be returned with the result
              if (!allErrors) gen.assign(valid, true);
            }, (e) => {
              gen.if((0, codegen_1._) `!(${e} instanceof ${it.ValidationError})`, () => gen.throw(e));
              addErrorsFrom(e);
              if (!allErrors) gen.assign(valid, false);
            });
            cxt.ok(valid);
          }
          function callSyncRef() {
            cxt.result((0, code_1.callValidateCode)(cxt, v, passCxt), () => addEvaluatedFrom(v), () => addErrorsFrom(v));
          }
          function addErrorsFrom(source) {
            const errs = (0, codegen_1._) `${source}.errors`;
            gen.assign(names_1.default.vErrors, (0, codegen_1._) `${names_1.default.vErrors} === null ? ${errs} : ${names_1.default.vErrors}.concat(${errs})`); // TODO tagged
            gen.assign(names_1.default.errors, (0, codegen_1._) `${names_1.default.vErrors}.length`);
          }
          function addEvaluatedFrom(source) {
            let _a;
            if (!it.opts.unevaluated) return;
            const schEvaluated = (_a = sch === null || sch === void 0 ? void 0 : sch.validate) === null || _a === void 0 ? void 0 : _a.evaluated;
            // TODO refactor
            if (it.props !== true) {
              if (schEvaluated && !schEvaluated.dynamicProps) {
                if (schEvaluated.props !== undefined) {
                  it.props = util_1.mergeEvaluated.props(gen, schEvaluated.props, it.props);
                }
              } else {
                const props = gen.var('props', (0, codegen_1._) `${source}.evaluated.props`);
                it.props = util_1.mergeEvaluated.props(gen, props, it.props, codegen_1.Name);
              }
            }
            if (it.items !== true) {
              if (schEvaluated && !schEvaluated.dynamicItems) {
                if (schEvaluated.items !== undefined) {
                  it.items = util_1.mergeEvaluated.items(gen, schEvaluated.items, it.items);
                }
              } else {
                const items = gen.var('items', (0, codegen_1._) `${source}.evaluated.items`);
                it.items = util_1.mergeEvaluated.items(gen, items, it.items, codegen_1.Name);
              }
            }
          }
        }
        exports.callRef = callRef;
        exports.default = def;
        // # sourceMappingURL=ref.js.map
        /***/ }),

      /***/ 1240:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const types_1 = __webpack_require__(9306);
        const compile_1 = __webpack_require__(5173);
        const util_1 = __webpack_require__(6776);
        const error = {
          message: ({ params: { discrError, tagName } }) => (discrError === types_1.DiscrError.Tag
            ? `tag "${tagName}" must be string`
            : `value of tag "${tagName}" must be in oneOf`),
          params: ({ params: { discrError, tag, tagName } }) => (0, codegen_1._) `{error: ${discrError}, tag: ${tagName}, tagValue: ${tag}}`,
        };
        const def = {
          keyword: 'discriminator',
          type: 'object',
          schemaType: 'object',
          error,
          code(cxt) {
            const { gen, data, schema, parentSchema, it } = cxt;
            const { oneOf } = parentSchema;
            if (!it.opts.discriminator) {
              throw new Error('discriminator: requires discriminator option');
            }
            const tagName = schema.propertyName;
            if (typeof tagName !== 'string') throw new Error('discriminator: requires propertyName');
            if (schema.mapping) throw new Error('discriminator: mapping is not supported');
            if (!oneOf) throw new Error('discriminator: requires oneOf keyword');
            const valid = gen.let('valid', false);
            const tag = gen.const('tag', (0, codegen_1._) `${data}${(0, codegen_1.getProperty)(tagName)}`);
            gen.if((0, codegen_1._) `typeof ${tag} == "string"`, () => validateMapping(), () => cxt.error(false, { discrError: types_1.DiscrError.Tag, tag, tagName }));
            cxt.ok(valid);
            function validateMapping() {
              const mapping = getMapping();
              gen.if(false);
              for (const tagValue in mapping) {
                gen.elseIf((0, codegen_1._) `${tag} === ${tagValue}`);
                gen.assign(valid, applyTagSchema(mapping[tagValue]));
              }
              gen.else();
              cxt.error(false, { discrError: types_1.DiscrError.Mapping, tag, tagName });
              gen.endIf();
            }
            function applyTagSchema(schemaProp) {
              const _valid = gen.name('valid');
              const schCxt = cxt.subschema({ keyword: 'oneOf', schemaProp }, _valid);
              cxt.mergeEvaluated(schCxt, codegen_1.Name);
              return _valid;
            }
            function getMapping() {
              let _a;
              const oneOfMapping = {};
              const topRequired = hasRequired(parentSchema);
              let tagRequired = true;
              for (let i = 0; i < oneOf.length; i++) {
                let sch = oneOf[i];
                if ((sch === null || sch === void 0 ? void 0 : sch.$ref) && !(0, util_1.schemaHasRulesButRef)(sch, it.self.RULES)) {
                  sch = compile_1.resolveRef.call(it.self, it.schemaEnv.root, it.baseId, sch === null || sch === void 0 ? void 0 : sch.$ref);
                  if (sch instanceof compile_1.SchemaEnv) sch = sch.schema;
                }
                const propSch = (_a = sch === null || sch === void 0 ? void 0 : sch.properties) === null || _a === void 0 ? void 0 : _a[tagName];
                if (typeof propSch !== 'object') {
                  throw new Error(`discriminator: oneOf subschemas (or referenced schemas) must have "properties/${tagName}"`);
                }
                tagRequired = tagRequired && (topRequired || hasRequired(sch));
                addMappings(propSch, i);
              }
              if (!tagRequired) throw new Error(`discriminator: "${tagName}" must be required`);
              return oneOfMapping;
              function hasRequired({ required }) {
                return Array.isArray(required) && required.includes(tagName);
              }
              function addMappings(sch, i) {
                if (sch.const) {
                  addMapping(sch.const, i);
                } else if (sch.enum) {
                  for (const tagValue of sch.enum) {
                    addMapping(tagValue, i);
                  }
                } else {
                  throw new Error(`discriminator: "properties/${tagName}" must have "const" or "enum"`);
                }
              }
              function addMapping(tagValue, i) {
                if (typeof tagValue !== 'string' || tagValue in oneOfMapping) {
                  throw new Error(`discriminator: "${tagName}" values must be unique strings`);
                }
                oneOfMapping[tagValue] = i;
              }
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=index.js.map
        /***/ }),

      /***/ 9306:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.DiscrError = void 0;
        let DiscrError;
        (function (DiscrError) {
          DiscrError.Tag = 'tag';
          DiscrError.Mapping = 'mapping';
        }(DiscrError = exports.DiscrError || (exports.DiscrError = {})));
        // # sourceMappingURL=types.js.map
        /***/ }),

      /***/ 3924:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const core_1 = __webpack_require__(9283);
        const validation_1 = __webpack_require__(2649);
        const applicator_1 = __webpack_require__(8200);
        const format_1 = __webpack_require__(9502);
        const metadata_1 = __webpack_require__(6167);
        const draft7Vocabularies = [
          core_1.default,
          validation_1.default,
          (0, applicator_1.default)(),
          format_1.default,
          metadata_1.metadataVocabulary,
          metadata_1.contentVocabulary,
        ];
        exports.default = draft7Vocabularies;
        // # sourceMappingURL=draft7.js.map
        /***/ }),

      /***/ 9651:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const error = {
          message: ({ schemaCode }) => (0, codegen_1.str) `must match format "${schemaCode}"`,
          params: ({ schemaCode }) => (0, codegen_1._) `{format: ${schemaCode}}`,
        };
        const def = {
          keyword: 'format',
          type: ['number', 'string'],
          schemaType: 'string',
          $data: true,
          error,
          code(cxt, ruleType) {
            const { gen, data, $data, schema, schemaCode, it } = cxt;
            const { opts, errSchemaPath, schemaEnv, self } = it;
            if (!opts.validateFormats) return;
            if ($data) validate$DataFormat();
            else validateFormat();
            function validate$DataFormat() {
              const fmts = gen.scopeValue('formats', {
                ref: self.formats,
                code: opts.code.formats,
              });
              const fDef = gen.const('fDef', (0, codegen_1._) `${fmts}[${schemaCode}]`);
              const fType = gen.let('fType');
              const format = gen.let('format');
              // TODO simplify
              gen.if((0, codegen_1._) `typeof ${fDef} == "object" && !(${fDef} instanceof RegExp)`, () => gen.assign(fType, (0, codegen_1._) `${fDef}.type || "string"`).assign(format, (0, codegen_1._) `${fDef}.validate`), () => gen.assign(fType, (0, codegen_1._) `"string"`).assign(format, fDef));
              cxt.fail$data((0, codegen_1.or)(unknownFmt(), invalidFmt()));
              function unknownFmt() {
                if (opts.strictSchema === false) return codegen_1.nil;
                return (0, codegen_1._) `${schemaCode} && !${format}`;
              }
              function invalidFmt() {
                const callFormat = schemaEnv.$async
                  ? (0, codegen_1._) `(${fDef}.async ? await ${format}(${data}) : ${format}(${data}))`
                  : (0, codegen_1._) `${format}(${data})`;
                const validData = (0, codegen_1._) `(typeof ${format} == "function" ? ${callFormat} : ${format}.test(${data}))`;
                return (0, codegen_1._) `${format} && ${format} !== true && ${fType} === ${ruleType} && !${validData}`;
              }
            }
            function validateFormat() {
              const formatDef = self.formats[schema];
              if (!formatDef) {
                unknownFormat();
                return;
              }
              if (formatDef === true) return;
              const [fmtType, format, fmtRef] = getFormat(formatDef);
              if (fmtType === ruleType) cxt.pass(validCondition());
              function unknownFormat() {
                if (opts.strictSchema === false) {
                  self.logger.warn(unknownMsg());
                  return;
                }
                throw new Error(unknownMsg());
                function unknownMsg() {
                  return `unknown format "${schema}" ignored in schema at path "${errSchemaPath}"`;
                }
              }
              function getFormat(fmtDef) {
                const code = fmtDef instanceof RegExp
                  ? (0, codegen_1.regexpCode)(fmtDef)
                  : opts.code.formats
                    ? (0, codegen_1._) `${opts.code.formats}${(0, codegen_1.getProperty)(schema)}`
                    : undefined;
                const fmt = gen.scopeValue('formats', { key: schema, ref: fmtDef, code });
                if (typeof fmtDef === 'object' && !(fmtDef instanceof RegExp)) {
                  return [fmtDef.type || 'string', fmtDef.validate, (0, codegen_1._) `${fmt}.validate`];
                }
                return ['string', fmtDef, fmt];
              }
              function validCondition() {
                if (typeof formatDef === 'object' && !(formatDef instanceof RegExp) && formatDef.async) {
                  if (!schemaEnv.$async) throw new Error('async format in sync schema');
                  return (0, codegen_1._) `await ${fmtRef}(${data})`;
                }
                return typeof format === 'function' ? (0, codegen_1._) `${fmtRef}(${data})` : (0, codegen_1._) `${fmtRef}.test(${data})`;
              }
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=format.js.map
        /***/ }),

      /***/ 9502:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const format_1 = __webpack_require__(9651);
        const format = [format_1.default];
        exports.default = format;
        // # sourceMappingURL=index.js.map
        /***/ }),

      /***/ 6167:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        exports.contentVocabulary = exports.metadataVocabulary = void 0;
        exports.metadataVocabulary = [
          'title',
          'description',
          'default',
          'deprecated',
          'readOnly',
          'writeOnly',
          'examples',
        ];
        exports.contentVocabulary = [
          'contentMediaType',
          'contentEncoding',
          'contentSchema',
        ];
        // # sourceMappingURL=metadata.js.map
        /***/ }),

      /***/ 4693:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const equal_1 = __webpack_require__(3510);
        const error = {
          message: 'must be equal to constant',
          params: ({ schemaCode }) => (0, codegen_1._) `{allowedValue: ${schemaCode}}`,
        };
        const def = {
          keyword: 'const',
          $data: true,
          error,
          code(cxt) {
            const { gen, data, $data, schemaCode, schema } = cxt;
            if ($data || (schema && typeof schema === 'object')) {
              cxt.fail$data((0, codegen_1._) `!${(0, util_1.useFunc)(gen, equal_1.default)}(${data}, ${schemaCode})`);
            } else {
              cxt.fail((0, codegen_1._) `${schema} !== ${data}`);
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=const.js.map
        /***/ }),

      /***/ 966:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const equal_1 = __webpack_require__(3510);
        const error = {
          message: 'must be equal to one of the allowed values',
          params: ({ schemaCode }) => (0, codegen_1._) `{allowedValues: ${schemaCode}}`,
        };
        const def = {
          keyword: 'enum',
          schemaType: 'array',
          $data: true,
          error,
          code(cxt) {
            const { gen, data, $data, schema, schemaCode, it } = cxt;
            if (!$data && schema.length === 0) throw new Error('enum must have non-empty array');
            const useLoop = schema.length >= it.opts.loopEnum;
            let eql;
            const getEql = () => (eql !== null && eql !== void 0 ? eql : (eql = (0, util_1.useFunc)(gen, equal_1.default)));
            let valid;
            if (useLoop || $data) {
              valid = gen.let('valid');
              cxt.block$data(valid, loopEnum);
            } else {
            /* istanbul ignore if */
              if (!Array.isArray(schema)) throw new Error('ajv implementation error');
              const vSchema = gen.const('vSchema', schemaCode);
              valid = (0, codegen_1.or)(...schema.map((_x, i) => equalCode(vSchema, i)));
            }
            cxt.pass(valid);
            function loopEnum() {
              gen.assign(valid, false);
              gen.forOf('v', schemaCode, v => gen.if((0, codegen_1._) `${getEql()}(${data}, ${v})`, () => gen.assign(valid, true).break()));
            }
            function equalCode(vSchema, i) {
              const sch = schema[i];
              return typeof sch === 'object' && sch !== null
                ? (0, codegen_1._) `${getEql()}(${data}, ${vSchema}[${i}])`
                : (0, codegen_1._) `${data} === ${sch}`;
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=enum.js.map
        /***/ }),

      /***/ 2649:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const limitNumber_1 = __webpack_require__(3983);
        const multipleOf_1 = __webpack_require__(430);
        const limitLength_1 = __webpack_require__(3229);
        const pattern_1 = __webpack_require__(4336);
        const limitProperties_1 = __webpack_require__(498);
        const required_1 = __webpack_require__(3301);
        const limitItems_1 = __webpack_require__(1687);
        const uniqueItems_1 = __webpack_require__(2958);
        const const_1 = __webpack_require__(4693);
        const enum_1 = __webpack_require__(966);
        const validation = [
          // number
          limitNumber_1.default,
          multipleOf_1.default,
          // string
          limitLength_1.default,
          pattern_1.default,
          // object
          limitProperties_1.default,
          required_1.default,
          // array
          limitItems_1.default,
          uniqueItems_1.default,
          // any
          { keyword: 'type', schemaType: ['string', 'array'] },
          { keyword: 'nullable', schemaType: 'boolean' },
          const_1.default,
          enum_1.default,
        ];
        exports.default = validation;
        // # sourceMappingURL=index.js.map
        /***/ }),

      /***/ 1687:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const error = {
          message({ keyword, schemaCode }) {
            const comp = keyword === 'maxItems' ? 'more' : 'fewer';
            return (0, codegen_1.str) `must NOT have ${comp} than ${schemaCode} items`;
          },
          params: ({ schemaCode }) => (0, codegen_1._) `{limit: ${schemaCode}}`,
        };
        const def = {
          keyword: ['maxItems', 'minItems'],
          type: 'array',
          schemaType: 'number',
          $data: true,
          error,
          code(cxt) {
            const { keyword, data, schemaCode } = cxt;
            const op = keyword === 'maxItems' ? codegen_1.operators.GT : codegen_1.operators.LT;
            cxt.fail$data((0, codegen_1._) `${data}.length ${op} ${schemaCode}`);
          },
        };
        exports.default = def;
        // # sourceMappingURL=limitItems.js.map
        /***/ }),

      /***/ 3229:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const ucs2length_1 = __webpack_require__(4499);
        const error = {
          message({ keyword, schemaCode }) {
            const comp = keyword === 'maxLength' ? 'more' : 'fewer';
            return (0, codegen_1.str) `must NOT have ${comp} than ${schemaCode} characters`;
          },
          params: ({ schemaCode }) => (0, codegen_1._) `{limit: ${schemaCode}}`,
        };
        const def = {
          keyword: ['maxLength', 'minLength'],
          type: 'string',
          schemaType: 'number',
          $data: true,
          error,
          code(cxt) {
            const { keyword, data, schemaCode, it } = cxt;
            const op = keyword === 'maxLength' ? codegen_1.operators.GT : codegen_1.operators.LT;
            const len = it.opts.unicode === false ? (0, codegen_1._) `${data}.length` : (0, codegen_1._) `${(0, util_1.useFunc)(cxt.gen, ucs2length_1.default)}(${data})`;
            cxt.fail$data((0, codegen_1._) `${len} ${op} ${schemaCode}`);
          },
        };
        exports.default = def;
        // # sourceMappingURL=limitLength.js.map
        /***/ }),

      /***/ 3983:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const ops = codegen_1.operators;
        const KWDs = {
          maximum: { okStr: '<=', ok: ops.LTE, fail: ops.GT },
          minimum: { okStr: '>=', ok: ops.GTE, fail: ops.LT },
          exclusiveMaximum: { okStr: '<', ok: ops.LT, fail: ops.GTE },
          exclusiveMinimum: { okStr: '>', ok: ops.GT, fail: ops.LTE },
        };
        const error = {
          message: ({ keyword, schemaCode }) => (0, codegen_1.str) `must be ${KWDs[keyword].okStr} ${schemaCode}`,
          params: ({ keyword, schemaCode }) => (0, codegen_1._) `{comparison: ${KWDs[keyword].okStr}, limit: ${schemaCode}}`,
        };
        const def = {
          keyword: Object.keys(KWDs),
          type: 'number',
          schemaType: 'number',
          $data: true,
          error,
          code(cxt) {
            const { keyword, data, schemaCode } = cxt;
            cxt.fail$data((0, codegen_1._) `${data} ${KWDs[keyword].fail} ${schemaCode} || isNaN(${data})`);
          },
        };
        exports.default = def;
        // # sourceMappingURL=limitNumber.js.map
        /***/ }),

      /***/ 498:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const error = {
          message({ keyword, schemaCode }) {
            const comp = keyword === 'maxProperties' ? 'more' : 'fewer';
            return (0, codegen_1.str) `must NOT have ${comp} than ${schemaCode} properties`;
          },
          params: ({ schemaCode }) => (0, codegen_1._) `{limit: ${schemaCode}}`,
        };
        const def = {
          keyword: ['maxProperties', 'minProperties'],
          type: 'object',
          schemaType: 'number',
          $data: true,
          error,
          code(cxt) {
            const { keyword, data, schemaCode } = cxt;
            const op = keyword === 'maxProperties' ? codegen_1.operators.GT : codegen_1.operators.LT;
            cxt.fail$data((0, codegen_1._) `Object.keys(${data}).length ${op} ${schemaCode}`);
          },
        };
        exports.default = def;
        // # sourceMappingURL=limitProperties.js.map
        /***/ }),

      /***/ 430:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const codegen_1 = __webpack_require__(3487);
        const error = {
          message: ({ schemaCode }) => (0, codegen_1.str) `must be multiple of ${schemaCode}`,
          params: ({ schemaCode }) => (0, codegen_1._) `{multipleOf: ${schemaCode}}`,
        };
        const def = {
          keyword: 'multipleOf',
          type: 'number',
          schemaType: 'number',
          $data: true,
          error,
          code(cxt) {
            const { gen, data, schemaCode, it } = cxt;
            // const bdt = bad$DataType(schemaCode, <string>def.schemaType, $data)
            const prec = it.opts.multipleOfPrecision;
            const res = gen.let('res');
            const invalid = prec
              ? (0, codegen_1._) `Math.abs(Math.round(${res}) - ${res}) > 1e-${prec}`
              : (0, codegen_1._) `${res} !== parseInt(${res})`;
            cxt.fail$data((0, codegen_1._) `(${schemaCode} === 0 || (${res} = ${data}/${schemaCode}, ${invalid}))`);
          },
        };
        exports.default = def;
        // # sourceMappingURL=multipleOf.js.map
        /***/ }),

      /***/ 4336:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const code_1 = __webpack_require__(412);
        const codegen_1 = __webpack_require__(3487);
        const error = {
          message: ({ schemaCode }) => (0, codegen_1.str) `must match pattern "${schemaCode}"`,
          params: ({ schemaCode }) => (0, codegen_1._) `{pattern: ${schemaCode}}`,
        };
        const def = {
          keyword: 'pattern',
          type: 'string',
          schemaType: 'string',
          $data: true,
          error,
          code(cxt) {
            const { data, $data, schema, schemaCode, it } = cxt;
            // TODO regexp should be wrapped in try/catchs
            const u = it.opts.unicodeRegExp ? 'u' : '';
            const regExp = $data ? (0, codegen_1._) `(new RegExp(${schemaCode}, ${u}))` : (0, code_1.usePattern)(cxt, schema);
            cxt.fail$data((0, codegen_1._) `!${regExp}.test(${data})`);
          },
        };
        exports.default = def;
        // # sourceMappingURL=pattern.js.map
        /***/ }),

      /***/ 3301:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const code_1 = __webpack_require__(412);
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const error = {
          message: ({ params: { missingProperty } }) => (0, codegen_1.str) `must have required property '${missingProperty}'`,
          params: ({ params: { missingProperty } }) => (0, codegen_1._) `{missingProperty: ${missingProperty}}`,
        };
        const def = {
          keyword: 'required',
          type: 'object',
          schemaType: 'array',
          $data: true,
          error,
          code(cxt) {
            const { gen, schema, schemaCode, data, $data, it } = cxt;
            const { opts } = it;
            if (!$data && schema.length === 0) return;
            const useLoop = schema.length >= opts.loopRequired;
            if (it.allErrors) allErrorsMode();
            else exitOnErrorMode();
            if (opts.strictRequired) {
              const props = cxt.parentSchema.properties;
              const { definedProperties } = cxt.it;
              for (const requiredKey of schema) {
                if ((props === null || props === void 0 ? void 0 : props[requiredKey]) === undefined && !definedProperties.has(requiredKey)) {
                  const schemaPath = it.schemaEnv.baseId + it.errSchemaPath;
                  const msg = `required property "${requiredKey}" is not defined at "${schemaPath}" (strictRequired)`;
                  (0, util_1.checkStrictMode)(it, msg, it.opts.strictRequired);
                }
              }
            }
            function allErrorsMode() {
              if (useLoop || $data) {
                cxt.block$data(codegen_1.nil, loopAllRequired);
              } else {
                for (const prop of schema) {
                  (0, code_1.checkReportMissingProp)(cxt, prop);
                }
              }
            }
            function exitOnErrorMode() {
              const missing = gen.let('missing');
              if (useLoop || $data) {
                const valid = gen.let('valid', true);
                cxt.block$data(valid, () => loopUntilMissing(missing, valid));
                cxt.ok(valid);
              } else {
                gen.if((0, code_1.checkMissingProp)(cxt, schema, missing));
                (0, code_1.reportMissingProp)(cxt, missing);
                gen.else();
              }
            }
            function loopAllRequired() {
              gen.forOf('prop', schemaCode, (prop) => {
                cxt.setParams({ missingProperty: prop });
                gen.if((0, code_1.noPropertyInData)(gen, data, prop, opts.ownProperties), () => cxt.error());
              });
            }
            function loopUntilMissing(missing, valid) {
              cxt.setParams({ missingProperty: missing });
              gen.forOf(missing, schemaCode, () => {
                gen.assign(valid, (0, code_1.propertyInData)(gen, data, missing, opts.ownProperties));
                gen.if((0, codegen_1.not)(valid), () => {
                  cxt.error();
                  gen.break();
                });
              }, codegen_1.nil);
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=required.js.map
        /***/ }),

      /***/ 2958:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        Object.defineProperty(exports, '__esModule', ({ value: true }));
        const dataType_1 = __webpack_require__(453);
        const codegen_1 = __webpack_require__(3487);
        const util_1 = __webpack_require__(6776);
        const equal_1 = __webpack_require__(3510);
        const error = {
          message: ({ params: { i, j } }) => (0, codegen_1.str) `must NOT have duplicate items (items ## ${j} and ${i} are identical)`,
          params: ({ params: { i, j } }) => (0, codegen_1._) `{i: ${i}, j: ${j}}`,
        };
        const def = {
          keyword: 'uniqueItems',
          type: 'array',
          schemaType: 'boolean',
          $data: true,
          error,
          code(cxt) {
            const { gen, data, $data, schema, parentSchema, schemaCode, it } = cxt;
            if (!$data && !schema) return;
            const valid = gen.let('valid');
            const itemTypes = parentSchema.items ? (0, dataType_1.getSchemaTypes)(parentSchema.items) : [];
            cxt.block$data(valid, validateUniqueItems, (0, codegen_1._) `${schemaCode} === false`);
            cxt.ok(valid);
            function validateUniqueItems() {
              const i = gen.let('i', (0, codegen_1._) `${data}.length`);
              const j = gen.let('j');
              cxt.setParams({ i, j });
              gen.assign(valid, true);
              gen.if((0, codegen_1._) `${i} > 1`, () => (canOptimize() ? loopN : loopN2)(i, j));
            }
            function canOptimize() {
              return itemTypes.length > 0 && !itemTypes.some(t => t === 'object' || t === 'array');
            }
            function loopN(i, j) {
              const item = gen.name('item');
              const wrongType = (0, dataType_1.checkDataTypes)(itemTypes, item, it.opts.strictNumbers, dataType_1.DataType.Wrong);
              const indices = gen.const('indices', (0, codegen_1._) `{}`);
              gen.for((0, codegen_1._) `;${i}--;`, () => {
                gen.let(item, (0, codegen_1._) `${data}[${i}]`);
                gen.if(wrongType, (0, codegen_1._) `continue`);
                if (itemTypes.length > 1) gen.if((0, codegen_1._) `typeof ${item} == "string"`, (0, codegen_1._) `${item} += "_"`);
                gen
                  .if((0, codegen_1._) `typeof ${indices}[${item}] == "number"`, () => {
                    gen.assign(j, (0, codegen_1._) `${indices}[${item}]`);
                    cxt.error();
                    gen.assign(valid, false).break();
                  })
                  .code((0, codegen_1._) `${indices}[${item}] = ${i}`);
              });
            }
            function loopN2(i, j) {
              const eql = (0, util_1.useFunc)(gen, equal_1.default);
              const outer = gen.name('outer');
              gen.label(outer).for((0, codegen_1._) `;${i}--;`, () => gen.for((0, codegen_1._) `${j} = ${i}; ${j}--;`, () => gen.if((0, codegen_1._) `${eql}(${data}[${i}], ${data}[${j}])`, () => {
                cxt.error();
                gen.assign(valid, false).break(outer);
              })));
            }
          },
        };
        exports.default = def;
        // # sourceMappingURL=uniqueItems.js.map
        /***/ }),

      /***/ 7794:
      /***/ (function (module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _node_modules_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(8081);
        /* harmony import */ const _node_modules_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /* #__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
        /* harmony import */ const _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(3645);
        /* harmony import */ const _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /* #__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
        // Imports


        const ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
        // Module
        ___CSS_LOADER_EXPORT___.push([module.id, '.bk-schema-form .mr24 {\n  margin-right: 24px;\n}\n\n.bk-schema-form .bk-form-item {\n  margin-top: unset !important;\n  margin-bottom: unset !important;\n}\n\n.bk-schema-form .bk-form-item .bk-form-content .group-text {\n  background-color: #f2f4f8;\n  height: 100%;\n}\n\n.bk-schema-form .bk-form-item .bk-select {\n  background-color: #fff;\n}\n\n.bk-schema-form .bk-form-item .bk-select.is-disabled {\n  background-color: #fafbfd;\n}\n\n.bk-schema-form .bk-schema-form-group.normal {\n  padding: 24px;\n  position: relative;\n}\n\n.bk-schema-form .bk-schema-form-group.card{\n  background: #fff;\n  padding: 0 24px 24px 24px;\n  border-radius: 2px;\n}\n\n.bk-schema-form .bk-schema-form-group.hide-empty-row .bk-schema-form-group-content {\n  row-gap: 0 !important;\n}\n\n.bk-schema-form .bk-schema-form-group.hide-empty-row .bk-schema-form-group-content .bk-form-item {\n  margin-bottom: 20px;\n}\n\n.bk-schema-form-group--error{\n  border-color: #f5222d !important;\n}\n\n.bk-schema-form-group__error-tips{\n  position: relative;\n  display: block;\n  width: 10px;\n  height: 10px;\n}\n\n.bk-schema-form-group__error-tips-popover {\n  position: absolute;\n  top: -5px;\n  left: 0;\n  z-index: 1;\n  background: #fff;\n  border: 1px solid #f5222d;\n  color: #f5222d;\n  font-size: 12px;\n  margin-left: 10px;\n  font-weight: normal;\n  padding: 5px 10px;\n  border-radius: 2px;\n  max-height: 50px;\n  overflow:hidden;\n}\n\n.bk-schema-form-group__error-tips-popover:hover {\n  max-height: unset;\n}\n\n.bk-schema-form-group__error-tips-popover > p {\n  padding: 0;\n  margin: 0;\n  white-space: nowrap;\n}\n\n.bk-schema-form .bk-schema-form-group .bk-schema-form-group-title {\n  font-size: 14px;\n  font-weight: 600;\n  color: #63656E;\n}\n\n.bk-schema-form .bk-schema-form-group .bk-schema-form-group-title.default {\n  display: inline-block;\n  margin-bottom: 10px;\n}\n\n.bk-schema-form .bk-schema-form-group .bk-schema-form-group-title.normal {\n  position: absolute;\n  top: -1em;\n  left:  10px;\n  line-height: 2em;\n  padding: 0 0.5em;\n  background: #fff;\n}\n\n.bk-schema-form .bk-schema-form-group .bk-schema-form-group-title.card{\n  display: flex;\n  height: 50px;\n  align-items: center;\n  padding: 0 24px;\n  margin: 0 -24px 8px -24px;\n}\n\n.bk-schema-form .bk-collapse-item .bk-collapse-item-header {\n  height: 54px;\n  padding: 0;\n}\n\n.bk-schema-form .bk-collapse-item .bk-collapse-item-content {\n  background: #f5f7fa;\n  padding: 0 34px 16px 34px;\n}\n\n.bk-schema-form .bk-schema-form-group-add {\n  font-size: 14px;\n  color: #3a84ff;\n  cursor: pointer;\n  display: flex;\n  align-items: center;\n}\n\n.bk-schema-form .bk-schema-form-group-delete {\n  position: absolute;\n  cursor: pointer;\n  color: #979bA5;\n}\n\n.bk-schema-form .bk-schema-form-group-delete:hover {\n  color: #3a84ff;\n}\n\n.bk-schema-form-item__error-tips {\n  color: #f5222d;\n  font-size: 12px;\n  margin-top: 5px;\n  margin: 0;\n  line-height: 1.5em;\n}\n\n.bk-schema-form-item--error input,\n.bk-schema-form-item--error .bk-textarea-wrapper,\n.bk-schema-form-item--error .bk-select {\n  border: 1px solid #f5222d;\n}\n\n.bk-schema-form .bk-schema-form-group .bk-form-unit-input .bk-textarea-wrapper {\n  min-height: 32px;\n}\n\n.bk-schema-form .bk-schema-form-group .bk-form-unit-input textarea {\n  min-height: 30px;\n}\n\n.bk-schema-form .bk-schema-form-item-auto-height .bk-form-content {\n  min-height: auto;\n  line-height: 1;\n}\n\n.bk-schema-form .table-widget-actions .action-btn {\n  margin-right: 8px;\n  font-size: 14px;\n  cursor: pointer;\n}\n.bk-schema-form .table-widget-actions .action-btn:hover {\n  color: #3a84ff;\n}\n.bk-schema-form .is-disabled .action-btn {\n  color: #dcdee5 !important;\n  cursor: not-allowed;\n}\n.bk-schema-form .bk-table-fixed-right {\n  height: 100% !important;\n  border-bottom: 1px solid #dfe0e5;\n}', '']);
        // Exports
        /* harmony default export */ __webpack_exports__.default = (___CSS_LOADER_EXPORT___);
        /***/ }),

      /***/ 3645:
      /***/ (function (module) {
        'use strict';


        /*
  MIT License http://www.opensource.org/licenses/mit-license.php
  Author Tobias Koppers @sokra
*/
        module.exports = function (cssWithMappingToString) {
          const list = [];

          // return the list of modules as css string
          list.toString = function toString() {
            return this.map((item) => {
              let content = '';
              const needLayer = typeof item[5] !== 'undefined';
              if (item[4]) {
                content += '@supports ('.concat(item[4], ') {');
              }
              if (item[2]) {
                content += '@media '.concat(item[2], ' {');
              }
              if (needLayer) {
                content += '@layer'.concat(item[5].length > 0 ? ' '.concat(item[5]) : '', ' {');
              }
              content += cssWithMappingToString(item);
              if (needLayer) {
                content += '}';
              }
              if (item[2]) {
                content += '}';
              }
              if (item[4]) {
                content += '}';
              }
              return content;
            }).join('');
          };

          // import a list of modules into the list
          list.i = function i(modules, media, dedupe, supports, layer) {
            if (typeof modules === 'string') {
              modules = [[null, modules, undefined]];
            }
            const alreadyImportedModules = {};
            if (dedupe) {
              for (let k = 0; k < this.length; k++) {
                const id = this[k][0];
                if (id != null) {
                  alreadyImportedModules[id] = true;
                }
              }
            }
            for (let _k = 0; _k < modules.length; _k++) {
              const item = [].concat(modules[_k]);
              if (dedupe && alreadyImportedModules[item[0]]) {
                continue;
              }
              if (typeof layer !== 'undefined') {
                if (typeof item[5] === 'undefined') {
                  item[5] = layer;
                } else {
                  item[1] = '@layer'.concat(item[5].length > 0 ? ' '.concat(item[5]) : '', ' {').concat(item[1], '}');
                  item[5] = layer;
                }
              }
              if (media) {
                if (!item[2]) {
                  item[2] = media;
                } else {
                  item[1] = '@media '.concat(item[2], ' {').concat(item[1], '}');
                  item[2] = media;
                }
              }
              if (supports) {
                if (!item[4]) {
                  item[4] = ''.concat(supports);
                } else {
                  item[1] = '@supports ('.concat(item[4], ') {').concat(item[1], '}');
                  item[4] = supports;
                }
              }
              list.push(item);
            }
          };
          return list;
        };
        /***/ }),

      /***/ 8081:
      /***/ (function (module) {
        'use strict';


        module.exports = function (i) {
          return i[1];
        };
        /***/ }),

      /***/ 4063:
      /***/ (function (module) {
        'use strict';


        // do not edit .js files directly - edit src/index.jst


        module.exports = function equal(a, b) {
          if (a === b) return true;

          if (a && b && typeof a === 'object' && typeof b === 'object') {
            if (a.constructor !== b.constructor) return false;

            let length; let i; let keys;
            if (Array.isArray(a)) {
              length = a.length;
              if (length != b.length) return false;
              for (i = length; i-- !== 0;) if (!equal(a[i], b[i])) return false;
              return true;
            }


            if (a.constructor === RegExp) return a.source === b.source && a.flags === b.flags;
            if (a.valueOf !== Object.prototype.valueOf) return a.valueOf() === b.valueOf();
            if (a.toString !== Object.prototype.toString) return a.toString() === b.toString();

            keys = Object.keys(a);
            length = keys.length;
            if (length !== Object.keys(b).length) return false;

            for (i = length; i-- !== 0;) if (!Object.prototype.hasOwnProperty.call(b, keys[i])) return false;

            for (i = length; i-- !== 0;) {
              const key = keys[i];

              if (!equal(a[key], b[key])) return false;
            }

            return true;
          }

          // true if both NaN, false otherwise
          return a !== a && b !== b;
        };
        /***/ }),

      /***/ 9461:
      /***/ (function (module) {
        'use strict';


        const traverse = module.exports = function (schema, opts, cb) {
          // Legacy support for v0.3.1 and earlier.
          if (typeof opts === 'function') {
            cb = opts;
            opts = {};
          }

          cb = opts.cb || cb;
          const pre = (typeof cb === 'function') ? cb : cb.pre || function () {};
          const post = cb.post || function () {};

          _traverse(opts, pre, post, schema, '', schema);
        };


        traverse.keywords = {
          additionalItems: true,
          items: true,
          contains: true,
          additionalProperties: true,
          propertyNames: true,
          not: true,
          if: true,
          then: true,
          else: true,
        };

        traverse.arrayKeywords = {
          items: true,
          allOf: true,
          anyOf: true,
          oneOf: true,
        };

        traverse.propsKeywords = {
          $defs: true,
          definitions: true,
          properties: true,
          patternProperties: true,
          dependencies: true,
        };

        traverse.skipKeywords = {
          default: true,
          enum: true,
          const: true,
          required: true,
          maximum: true,
          minimum: true,
          exclusiveMaximum: true,
          exclusiveMinimum: true,
          multipleOf: true,
          maxLength: true,
          minLength: true,
          pattern: true,
          format: true,
          maxItems: true,
          minItems: true,
          uniqueItems: true,
          maxProperties: true,
          minProperties: true,
        };


        function _traverse(opts, pre, post, schema, jsonPtr, rootSchema, parentJsonPtr, parentKeyword, parentSchema, keyIndex) {
          if (schema && typeof schema === 'object' && !Array.isArray(schema)) {
            pre(schema, jsonPtr, rootSchema, parentJsonPtr, parentKeyword, parentSchema, keyIndex);
            for (const key in schema) {
              const sch = schema[key];
              if (Array.isArray(sch)) {
                if (key in traverse.arrayKeywords) {
                  for (let i = 0; i < sch.length; i++) _traverse(opts, pre, post, sch[i], `${jsonPtr}/${key}/${i}`, rootSchema, jsonPtr, key, schema, i);
                }
              } else if (key in traverse.propsKeywords) {
                if (sch && typeof sch === 'object') {
                  for (const prop in sch) _traverse(opts, pre, post, sch[prop], `${jsonPtr}/${key}/${escapeJsonPtr(prop)}`, rootSchema, jsonPtr, key, schema, prop);
                }
              } else if (key in traverse.keywords || (opts.allKeys && !(key in traverse.skipKeywords))) {
                _traverse(opts, pre, post, sch, `${jsonPtr}/${key}`, rootSchema, jsonPtr, key, schema);
              }
            }
            post(schema, jsonPtr, rootSchema, parentJsonPtr, parentKeyword, parentSchema, keyIndex);
          }
        }


        function escapeJsonPtr(str) {
          return str.replace(/~/g, '~0').replace(/\//g, '~1');
        }
        /***/ }),

      /***/ 6620:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _util_fetch__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(374);


        /* harmony default export */ __webpack_exports__.default = ({
          // 当前项shema
          schema: {
            type: Object,
            default: () => ({}),
          },
          // 当前路径（唯一标识）
          path: {
            type: String,
            default: '',
          },
          // 是否必须字段
          required: {
            type: Boolean,
            default: false,
          },
          // 全量数据（只读）
          rootData: {
            type: Object,
            default: () => ({}),
          },
          // 当前值
          modelValue: {
            type: [String, Number, Array, Object, Boolean],
          },
          // 布局配置
          layout: {
            type: Object,
            default: () => ({}),
          },
          // 当前全局变量上下文
          context: {
            type: Object,
            default: () => ({}),
          },
          // 当前项是否可移除
          removeable: {
            type: Boolean,
            default: false,
          },
          // http请求适配器
          httpAdapter: {
            type: Object,
            default: () => ({
              request: _util_fetch__WEBPACK_IMPORTED_MODULE_0__/* ["default"] */ .Z,
              // 请求方法
              responseParse: res => res,
              // fetch请求返回数据通用解析函数
              // responseParse: {
              //   dataKey: 'data',
              //   valueKey: 'value',
              //   labelKey: 'label',
              // }, // 也可以是对像形式
            }),
          },
          visible: {
            type: Boolean,
            default: true,
          },
          error: {
            type: Boolean,
            default: false,
          },
          disabled: {
            type: Boolean,
            default: false,
          },
          readonly: {
            type: Boolean,
            default: false,
          },
          readonlyMode: {
            type: String,
            default: 'value',
            validator: value => ['value', 'custom'].includes(value),
          },
        });
        /***/ }),

      /***/ 1975:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        // ESM COMPAT FLAG
        __webpack_require__.r(__webpack_exports__);

        // EXPORTS
        __webpack_require__.d(__webpack_exports__, {
          default() {
            return /* binding */ ArrayWidget;
          },
        });

        // EXTERNAL MODULE: ./src/core/schema.ts
        const schema = __webpack_require__(8683);
        // EXTERNAL MODULE: external "vue"
        const external_vue_ = __webpack_require__(748);
        // EXTERNAL MODULE: ./src/adapter/field/FieldProps.ts
        const FieldProps = __webpack_require__(6620);
        // EXTERNAL MODULE: ./src/util/index.ts
        const util = __webpack_require__(1851);
        // EXTERNAL MODULE: ./src/adapter/field/SchemaField.tsx
        const SchemaField = __webpack_require__(799);
        // EXTERNAL MODULE: ./src/core/path.ts
        const core_path = __webpack_require__(4879);
        // EXTERNAL MODULE: ./src/core/register.ts
        const register = __webpack_require__(7859);
        ;// CONCATENATED MODULE: ./src/core/lang.ts


        const messages = {
          'zh-CN': {
            add: '\u6DFB\u52A0',
          },
          'en-US': {
            add: 'Add',
          },
        };
        function locale(item) {
          let _a;
          let curLang = (0, util.getCookie)('blueking_language') || 'zh-CN';
          if (['en-US', 'enUS', 'enus', 'en-us', 'en'].includes(curLang)) {
            curLang = 'en-US';
          } else {
            curLang = 'zh-CN';
          }
          return ((_a = messages[curLang]) == null ? void 0 : _a[item]) || '';
        }

        ;// CONCATENATED MODULE: ./src/adapter/widget/ArrayWidget.ts

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
        const __objRest = (source, exclude) => {
          const target = {};
          for (var prop in source) if (__hasOwnProp.call(source, prop) && exclude.indexOf(prop) < 0) target[prop] = source[prop];
          if (source != null && __getOwnPropSymbols) for (var prop of __getOwnPropSymbols(source)) {
            if (exclude.indexOf(prop) < 0 && __propIsEnum.call(source, prop)) target[prop] = source[prop];
          }
          return target;
        };


        /* harmony default export */ var ArrayWidget = ((0, external_vue_.defineComponent)({
          name: 'ArrayWidget',
          props: __spreadProps(__spreadValues({}, FieldProps.default), {
            modelValue: {
              type: Array,
              default: () => [],
            },
          }),
          mounted() {
            this.handleFillItem();
          },
          methods: {
            // 补全minItems项
            handleFillItem() {
              const { minItems = 0 } = this.schema;
              const valueLen = this.modelValue ? this.modelValue.length : 0;
              if (valueLen < minItems) {
                const data = schema.default.getSchemaDefaultValue(this.schema.items);
                const remainData = new Array(minItems - valueLen).fill(data);
                this.$emit('update:modelValue', { path: this.path, value: [
                  ...this.modelValue || [],
                  ...remainData,
                ] });
              }
            },
            // 添加item
            handleAddItem() {
              const data = schema.default.getSchemaDefaultValue(this.schema.items);
              const value = JSON.parse(JSON.stringify(this.modelValue || []));
              value.push(data);
              this.$emit('update:modelValue', { path: this.path, value });
            },
            // 删除item
            handleDeleteItem(path) {
              const index = Number(core_path.default.getPathLastProp(path));
              const value = JSON.parse(JSON.stringify(this.modelValue || []));
              value.splice(index, 1);
              this.$emit('update:modelValue', { path: this.path, value });
            },
          },
          render() {
            const self = this;
            const arrVnodeList = (Array.isArray(this.modelValue) ? this.modelValue : []).map((_, index) => {
              const curPath = core_path.default.getCurPath(this.path, index);
              return (0, external_vue_.h)(
                SchemaField.default,
                __spreadProps(__spreadValues(__spreadValues({}, this.$props), this.$attrs), {
                  key: `${curPath}-${this.modelValue.length}`,
                  // 加上数组长度作为key，防止diff时出现复用组件问题
                  schema: this.schema.items,
                  path: curPath,
                  layout: __spreadProps(__spreadValues({}, this.layout), {
                    item: {},
                    // todo: 暂时不支持数组项之间的布局
                  }),
                  removeable: true,
                  onRemove(path) {
                    self.handleDeleteItem(path);
                  },
                }),
              );
            });
            const _a = schema.default.getGroupWrap(this.schema); const { name } = _a; const vnode = __objRest(_a, ['name']);
            return (0, external_vue_.h)(
              name,
              (0, util.mergeDeep)(__spreadProps(__spreadValues({}, this.$props), {
                layout: {},
                // 数组类型的容器布局在每个数组项内控制
                showTitle: true,
                // 数组类型默认展示分组title
                style: __spreadValues({}, this.layout.item || {}),
              }), vnode),
              [
                ...arrVnodeList,
                (0, external_vue_.h)(
                  register.default.getBaseWidget('form-item'),
                  {
                    class: {
                      'bk-schema-form-item-auto-height': true,
                    },
                  },
                  [
                    (0, external_vue_.h)('span', {
                      class: ['bk-schema-form-group-add'],
                      onClick() {
                        self.handleAddItem();
                      },
                    }, [
                      (0, external_vue_.h)('i', {
                        class: ['bk-icon icon-plus-circle-shape mr5'],
                      }),
                      locale('add'),
                    ]),
                  ],
                ),
              ],
            );
          },
        }));
        /***/ }),

      /***/ 8194:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(7859);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_1__);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_1__.defineComponent)({
          name: 'ButtonWidget',
          props: {
            word: {
              type: String,
              default: '',
            },
          },
          methods: {
            handleClick() {
              this.$emit('click');
            },
          },
          render() {
            const self = this;
            return (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(_core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('button'), __spreadProps(__spreadValues({}, this.$attrs), {
              onClick: self.handleClick(),
            }), this.word);
          },
        }));
        /***/ }),

      /***/ 5341:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(7859);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_1__);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_1__.defineComponent)({
          name: 'CheckboxWidget',
          props: {
            datasource: {
              type: Array,
              default: () => [],
            },
            modelValue: {
              type: [Array, Boolean],
              default: () => [],
            },
            // 单个checkbox时文案
            label: {
              type: String,
              default: '',
            },
          },
          methods: {
            handleChange(val) {
              this.$emit('update:modelValue', val);
            },
          },
          render() {
            return Array.isArray(this.modelValue) ? (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(
              _core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('checkbox-group'),
              {
                modelValue: this.modelValue,
                onChange: this.handleChange,
              },
              this.datasource.map(item => (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(
                _core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('checkbox'),
                __spreadProps(__spreadValues({}, this.$attrs), {
                  key: item.value,
                  class: ['mr24'],
                  modelValue: item.value,
                }),
                item.label,
              )),
            ) : (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(_core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('checkbox'), {
              modelValue: this.modelValue,
              onChange: this.handleChange,
            }, this.label);
          },
        }));
        /***/ }),

      /***/ 1272:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _core_layout__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(3570);
        /* harmony import */ const _core_path__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(4879);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(7859);
        /* harmony import */ const _core_schema__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(8683);
        /* harmony import */ const _util__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(1851);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_5___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_5__);
        /* harmony import */ const _common_FieldGroupWrap__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(2402);
        /* harmony import */ const _field_FieldProps__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(6620);
        /* harmony import */ const _field_SchemaField__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(799);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_5__.defineComponent)({
          name: 'CollapseWidget',
          props: __spreadProps(__spreadValues({}, _field_FieldProps__WEBPACK_IMPORTED_MODULE_7__.default), {
            type: {
              type: String,
              default: 'default',
              validator: value => ['default', 'normal', 'card'].includes(value),
            },
            showTitle: {
              type: Boolean,
              default: false,
            },
            border: {
              type: Boolean,
              default: false,
            },
            defaultActiveName: {
              type: Array,
              default: () => [],
            },
            verifiable: {
              type: Boolean,
              default: false,
            },
          }),
          data() {
            return {
              activeName: this.defaultActiveName,
            };
          },
          render() {
            let _a;
            const collapseStyle = {};
            const collapseTitleStyle = {
              background: '#f5f7fa',
              'border-radius': '2px',
              padding: '0 14px',
              height: '100%',
              display: 'flex',
              'align-items': 'center',
            };
            const collapseIconStyle = {
              'font-size': '16px',
              display: 'inline-block',
              transition: 'all 0.5s ease',
            };
            const groupWrapProps = __spreadProps(__spreadValues({}, this.$props), {
              layout: __spreadProps(__spreadValues({}, this.layout), {
                container: {},
                // Tab组的容器layout由panel内容控制
              }),
              title: this.schema.title,
            });
            const properties = (0, _util__WEBPACK_IMPORTED_MODULE_4__.orderProperties)(Object.keys(((_a = this.schema) == null ? void 0 : _a.properties) || {}), this.schema['ui:order']);
            const collapseItems = properties.map((key) => {
              let _a2; let _b;
              const schemaItem = (_b = (_a2 = this.schema) == null ? void 0 : _a2.properties) == null ? void 0 : _b[key];
              const curPath = _core_path__WEBPACK_IMPORTED_MODULE_1__.default.getCurPath(this.path, key);
              const lastProp = curPath.split('.').pop();
              const layoutConfig = _core_layout__WEBPACK_IMPORTED_MODULE_0__.default.findLayoutByProp(lastProp, this.layout.group || []) || {};
              return (0, vue__WEBPACK_IMPORTED_MODULE_5__.h)(
                _core_register__WEBPACK_IMPORTED_MODULE_2__.default.getBaseWidget('collapse-item'),
                {
                  key,
                  hideArrow: true,
                  name: key,
                  class: ['mb15'],
                },
                [
                  (0, vue__WEBPACK_IMPORTED_MODULE_5__.h)(
                    'div',
                    {
                      style: collapseTitleStyle,
                    },
                    [
                      (0, vue__WEBPACK_IMPORTED_MODULE_5__.h)('i', {
                        class: ['bk-icon icon-down-shape mr5'],
                        style: __spreadProps(__spreadValues({}, collapseIconStyle), {
                          transform: this.activeName.includes(key) ? 'rotate(0deg)' : 'rotate(-90deg)',
                        }),
                      }),
                      schemaItem.title,
                    ],
                  ),
                  (0, vue__WEBPACK_IMPORTED_MODULE_5__.h)(
                    'template',
                    {},
                    {
                      content: () => (0, vue__WEBPACK_IMPORTED_MODULE_5__.h)(_field_SchemaField__WEBPACK_IMPORTED_MODULE_8__.default, __spreadProps(__spreadValues(__spreadValues({
                        key: curPath,
                      }, this.$props), this.$attrs), {
                        schema: schemaItem,
                        required: _core_schema__WEBPACK_IMPORTED_MODULE_3__.default.isRequired(schemaItem, key),
                        path: curPath,
                        layout: layoutConfig,
                        removeable: false,
                        // todo: 不往下传递可删除属性
                      })),
                    },
                  ),
                ],
              );
            });
            const self = this;
            return (0, vue__WEBPACK_IMPORTED_MODULE_5__.h)(
              _common_FieldGroupWrap__WEBPACK_IMPORTED_MODULE_6__.default,
              __spreadValues({}, groupWrapProps),
              [
                (0, vue__WEBPACK_IMPORTED_MODULE_5__.h)(
                  _core_register__WEBPACK_IMPORTED_MODULE_2__.default.getBaseWidget('collapse'),
                  {
                    style: collapseStyle,
                    modelValue: this.activeName,
                    'onUpdate:modelValue'(actives) {
                      self.activeName = actives;
                    },
                  },
                  collapseItems,
                ),
              ],
            );
          },
        }));
        /***/ }),

      /***/ 9376:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(7859);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_1__);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_1__.defineComponent)({
          name: 'ColorPicker',
          props: {
            modelValue: String,
          },
          methods: {
            handleChange(color) {
              this.$emit('update:modelValue', color);
            },
          },
          render() {
            return (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(_core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('color-picker'), __spreadProps(__spreadValues({}, this.$attrs), {
              modelValue: this.modelValue,
              onChange: this.handleChange,
            }));
          },
        }));
        /***/ }),

      /***/ 9442:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(7859);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_1__);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_1__.defineComponent)({
          name: 'InputWidget',
          props: {
            modelValue: [String, Number],
            unit: {
              type: String,
              default: '',
            },
            maxRows: {
              type: Number,
              default: 0,
            },
          },
          computed: {
            rows() {
              const len = String(this.modelValue).split('\n').length;
              return len <= this.maxRows ? len : this.maxRows;
            },
          },
          methods: {
            handleInput(v) {
              if (this.$attrs.type === 'number') {
                this.$emit('update:modelValue', isNaN(v) || v === '' ? v : Number(v));
              } else {
                this.$emit('update:modelValue', v);
              }
            },
            handleBlur(v) {
              if (this.$attrs.type === 'number' && isNaN(v)) {
                this.$emit('update:modelValue', this.$attrs.min || 0);
              }
            },
          },
          render() {
            return (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(
              _core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('input'),
              __spreadProps(__spreadValues({}, this.$attrs), {
                modelValue: this.modelValue,
                rows: this.rows,
                type: this.maxRows > 1 || Number(this.$attrs.rows) > 1 ? 'textarea' : 'text',
                class: ['bk-form-unit-input'],
                'onUpdate:modelValue': this.handleInput,
                onBlur: this.handleBlur,
              }),
              {
                append: () => (this.unit ? (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(
                  'div',
                  {
                    class: ['group-text'],
                  },
                  this.unit,
                ) : null),
              },
            );
          },
        }));
        /***/ }),

      /***/ 2544:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(7859);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_1__);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_1__.defineComponent)({
          name: 'RadioWidget',
          props: {
            datasource: {
              type: Array,
              default: () => [],
            },
            modelValue: {
              type: [String, Number, Boolean],
              default: '',
            },
            disabled: {
              type: Boolean,
              default: false,
            },
          },
          methods: {
            handleChange(val) {
              this.$emit('update:modelValue', val);
            },
          },
          render() {
            return (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(
              _core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('radio-group'),
              __spreadProps(__spreadValues({}, this.$attrs), {
                modelValue: this.modelValue,
                onChange: this.handleChange,
              }),
              {
                default: () => this.datasource.map(item => (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(
                  _core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('radio'),
                  {
                    key: item.value,
                    class: ['mr24'],
                    modelValue: item.value,
                    label: item.value,
                    disabled: item.disabled || this.disabled,
                  },
                  {
                    default: () => item.label,
                  },
                )),
              },
            );
          },
        }));
        /***/ }),

      /***/ 8985:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(7859);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_1__);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_1__.defineComponent)({
          name: 'SelectWidget',
          props: {
            datasource: {
              type: Array,
              default: () => [],
            },
            modelValue: {
              type: [Array, String, Number, Boolean],
              default: '',
            },
            loading: {
              type: Boolean,
              default: false,
            },
          },
          methods: {
            handleSelectChange(val) {
              this.$emit('update:modelValue', val);
            },
          },
          render() {
            return (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(
              _core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('select'),
              __spreadProps(__spreadValues({}, this.$attrs), {
                loading: this.loading,
                modelValue: this.modelValue,
                onChange: this.handleSelectChange,
              }),
              {
                default: () => {
                  let _a;
                  return (_a = this.datasource) == null ? void 0 : _a.map(item => (0, vue__WEBPACK_IMPORTED_MODULE_1__.withDirectives)(
                    (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(
                      _core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('option'),
                      {
                        key: item.value,
                        name: item.label,
                        id: item.value,
                        disabled: item.disabled,
                      },
                    ),
                    [
                      // todo
                      // {
                      //   name: 'bk-tooltips',
                      //   value: {
                      //     content: item.tips,
                      //     disabled: !item.tips,
                      //     placement: 'right',
                      //     boundary: 'window',
                      //   },
                      // },
                    ],
                  ));
                },
              },
            );
          },
        }));
        /***/ }),

      /***/ 5638:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(7859);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_1___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_1__);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_1__.defineComponent)({
          name: 'SwitchWidget',
          props: {
            modelValue: Boolean,
          },
          methods: {
            handleChange(v) {
              this.$emit('update:modelValue', v);
            },
          },
          render() {
            return (0, vue__WEBPACK_IMPORTED_MODULE_1__.h)(
              _core_register__WEBPACK_IMPORTED_MODULE_0__.default.getBaseWidget('switcher'),
              __spreadProps(__spreadValues({}, this.$attrs), {
                modelValue: this.modelValue,
                onChange: (v) => {
                  this.handleChange(v);
                },
              }),
            );
          },
        }));
        /***/ }),

      /***/ 5307:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_0___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_0__);
        /* harmony import */ const _field_FieldProps__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(6620);
        /* harmony import */ const _common_FieldGroupWrap__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(2402);
        /* harmony import */ const _field_SchemaField__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(799);
        /* harmony import */ const _core_schema__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(8683);
        /* harmony import */ const _core_path__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(4879);
        /* harmony import */ const _core_layout__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(3570);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(7859);
        /* harmony import */ const _util__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(1851);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_0__.defineComponent)({
          name: 'TabWidget',
          props: __spreadProps(__spreadValues({}, _field_FieldProps__WEBPACK_IMPORTED_MODULE_1__.default), {
            type: {
              type: String,
              default: 'default',
              validator: value => ['default', 'normal', 'card'].includes(value),
            },
            showTitle: {
              type: Boolean,
              default: false,
            },
            border: {
              type: Boolean,
              default: false,
            },
            verifiable: {
              type: Boolean,
              default: false,
            },
          }),
          render() {
            let _a;
            const groupWrapProps = __spreadProps(__spreadValues({}, this.$props), {
              layout: __spreadProps(__spreadValues({}, this.layout), {
                container: {},
                // Tab组的容器layout由panel内容控制
              }),
              title: this.schema.title,
            });
            const self = this;
            const properties = (0, _util__WEBPACK_IMPORTED_MODULE_8__.orderProperties)(Object.keys(((_a = this.schema) == null ? void 0 : _a.properties) || {}), this.schema['ui:order']);
            return (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)(
              _common_FieldGroupWrap__WEBPACK_IMPORTED_MODULE_2__.default,
              __spreadProps(__spreadValues({}, groupWrapProps), {
                onRemove(path) {
                  self.$emit('remove', path);
                },
              }),
              [
                (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)(
                  _core_register__WEBPACK_IMPORTED_MODULE_7__.default.getBaseWidget('tab'),
                  {},
                  properties.map((key) => {
                    let _a2; let _b;
                    const schemaItem = (_b = (_a2 = this.schema) == null ? void 0 : _a2.properties) == null ? void 0 : _b[key];
                    const curPath = _core_path__WEBPACK_IMPORTED_MODULE_5__.default.getCurPath(this.path, key);
                    const lastProp = curPath.split('.').pop();
                    const layoutConfig = _core_layout__WEBPACK_IMPORTED_MODULE_6__.default.findLayoutByProp(lastProp, this.layout.group || []) || {};
                    return (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)(
                      _core_register__WEBPACK_IMPORTED_MODULE_7__.default.getBaseWidget('tab-panel'),
                      {
                        key,
                        name: key,
                        label: schemaItem == null ? void 0 : schemaItem.title,
                      },
                      [
                        (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)(
                          _field_SchemaField__WEBPACK_IMPORTED_MODULE_3__.default,
                          __spreadProps(__spreadValues(__spreadValues({}, this.$props), this.$attrs), {
                            key: curPath,
                            schema: schemaItem,
                            required: _core_schema__WEBPACK_IMPORTED_MODULE_4__.default.isRequired(schemaItem, key),
                            path: curPath,
                            layout: layoutConfig,
                            removeable: false,
                            // todo: 不往下传递可删除属性
                          }),
                        ),
                      ],
                    );
                  }),
                ),
              ],
            );
          },
        }));
        /***/ }),

      /***/ 294:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_0___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_0__);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(7859);
        /* harmony import */ const _util__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(1851);
        /* harmony import */ const _core_schema__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(8683);
        /* harmony import */ const _core_path__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(4879);
        /* harmony import */ const _field_FieldProps__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(6620);
        /* harmony import */ const _field_SchemaField__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(799);
        /* harmony import */ const _core_widgetTree__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(7564);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));


        const getRowDefaultData = (properties = {}) => {
          const keys = Object.keys(properties);
          const data = {};
          keys.forEach((key) => {
            data[key] = _core_schema__WEBPACK_IMPORTED_MODULE_3__.default.getSchemaDefaultValue(properties[key]);
          });
          return [data];
        };
        /* harmony default export */ __webpack_exports__.default = ((0, vue__WEBPACK_IMPORTED_MODULE_0__.defineComponent)({
          name: 'TableWidget',
          props: __spreadProps(__spreadValues({}, _field_FieldProps__WEBPACK_IMPORTED_MODULE_5__.default), {
            // 当前值
            modelValue: {
              type: Array,
            },
          }),
          watch: {
            modelValue: {
              immediate: true,
              handler() {
                let _a;
                (_a = this.modelValue) == null ? void 0 : _a.forEach((_, index) => {
                  const path = `${this.path}.${index}`;
                  _core_widgetTree__WEBPACK_IMPORTED_MODULE_7__.default.removeWidgetNode(path, null);
                  _core_widgetTree__WEBPACK_IMPORTED_MODULE_7__.default.addWidgetNode(path, null, 'group');
                });
              },
            },
          },
          methods: {
            // 单元格表单编辑
            handleCellValChange({ path, value }) {
              const subPath = _core_path__WEBPACK_IMPORTED_MODULE_4__.default.getSubPath(this.path, path);
              const newValue = _core_path__WEBPACK_IMPORTED_MODULE_4__.default.setPathValue(this.modelValue, subPath, value);
              this.$emit('update:modelValue', newValue);
            },
            // 新增
            handleAddRow(index) {
              let _a; let _b; let _c;
              if ((_a = this.schema['ui:props']) == null ? void 0 : _a.disabled) return;
              const newValue = ((_b = this.modelValue) == null ? void 0 : _b.slice(0)) || [];
              newValue.splice(index + 1, 0, ...getRowDefaultData((_c = this.$props.schema.items) == null ? void 0 : _c.properties));
              this.$emit('update:modelValue', newValue);
            },
            // 删除
            handleDelRow(index) {
              let _a; let _b;
              if ((_a = this.schema['ui:props']) == null ? void 0 : _a.disabled) return;
              const newValue = ((_b = this.modelValue) == null ? void 0 : _b.slice(0)) || [];
              newValue.splice(index, 1);
              this.$emit('update:modelValue', newValue);
            },
          },
          render() {
            const self = this;
            const { schema, path, modelValue } = this;
            const schemaItems = schema.items;
            let properties = {};
            if (schemaItems == null ? void 0 : schemaItems.properties) {
              properties = schemaItems == null ? void 0 : schemaItems.properties;
            } else {
              console.warn('The current schema type is not supported table component', schemaItems);
            }
            const uiOptions = _core_schema__WEBPACK_IMPORTED_MODULE_3__.default.getUiOptions(schema);
            const getTableColumns = () => {
              const columnList = Object.keys(properties).map((field) => {
                const colField = properties[field];
                const colProps = colField['ui:props'] || {};
                return __spreadProps(__spreadValues({}, colProps), {
                  label: colField == null ? void 0 : colField.title,
                  field,
                  render: ({ row, index }) => (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)(
                    _field_SchemaField__WEBPACK_IMPORTED_MODULE_6__.default,
                    __spreadProps(__spreadValues({}, this.$props), {
                      schema: (0, _util__WEBPACK_IMPORTED_MODULE_2__.mergeDeep)(
                        colField,
                        {
                          'ui:props': {
                            // 默认不展示标题
                            showTitle: false,
                            // 0.1 兼容formItem设置 labelWidth 0 不生效问题
                            labelWidth: 0.1,
                          },
                        },
                      ),
                      path: _core_path__WEBPACK_IMPORTED_MODULE_4__.default.getCurPath(path, `${index}.${field}`),
                      modelValue: row[field],
                      'onUpdate:modelValue'(data) {
                        self.handleCellValChange(data);
                      },
                    }),
                  ),
                });
              });
              if (!this.readonly && uiOptions.modifyRows !== false) {
                columnList.push({
                  label: '\u64CD\u4F5C',
                  width: 100,
                  fixed: 'right',
                  render: ({ index }) => {
                    let _a;
                    return (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)(
                      'div',
                      {
                        class: {
                          'table-widget-actions': true,
                          'is-disabled': (_a = schema['ui:props']) == null ? void 0 : _a.disabled,
                        },
                      },
                      {
                        default: () => [
                          (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)('i', {
                            class: 'bk-icon icon-plus-circle action-btn',
                            onClick() {
                              self.handleAddRow(index);
                            },
                          }),
                          (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)('i', {
                            class: 'bk-icon icon-minus-circle action-btn',
                            onClick() {
                              self.handleDelRow(index);
                            },
                          }),
                        ],
                      },
                    );
                  },
                });
              }
              return columnList;
            };
            return (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)(
              _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getBaseWidget('table'),
              __spreadProps(__spreadValues({}, schema['ui:component'] || {}), {
                data: modelValue,
                columns: getTableColumns(),
              }),
              {
                empty: () => (this.readonly || uiOptions.modifyRows === false ? null : (0, vue__WEBPACK_IMPORTED_MODULE_0__.h)(
                  'div',
                  {
                    style: {
                      color: '#3a84ff',
                      cursor: 'pointer',
                    },
                    onClick: () => {
                      self.handleAddRow(0);
                    },
                  },
                  '\u70B9\u51FB\u6DFB\u52A0\u6570\u636E',
                )),
              },
            );
          },
        }));
        /***/ }),

      /***/ 5421:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        // ESM COMPAT FLAG
        __webpack_require__.r(__webpack_exports__);

        // EXPORTS
        __webpack_require__.d(__webpack_exports__, {
          default() {
            return /* binding */ Widget;
          },
        });

        // EXTERNAL MODULE: ./src/core/schema.ts
        const schema = __webpack_require__(8683);
        // EXTERNAL MODULE: ./src/core/register.ts
        const register = __webpack_require__(7859);
        // EXTERNAL MODULE: external "vue"
        const external_vue_ = __webpack_require__(748);
        // EXTERNAL MODULE: ./src/util/index.ts
        const util = __webpack_require__(1851);
        // EXTERNAL MODULE: ./src/adapter/field/FieldProps.ts
        const FieldProps = __webpack_require__(6620);
        // EXTERNAL MODULE: ./src/core/path.ts
        const core_path = __webpack_require__(4879);
        // EXTERNAL MODULE: ./src/core/expression.ts
        const expression = __webpack_require__(8343);
        // EXTERNAL MODULE: ./src/core/widgetTree.ts
        const widgetTree = __webpack_require__(7564);
        ;// CONCATENATED MODULE: ./src/core/reaction.ts


        const reactionsMap = {};
        const subscribe = (path, typeName, fn) => {
          if (!reactionsMap[path]) {
            reactionsMap[path] = {
              lifetime: {},
              effect: {},
              fns: [],
            };
          }
          if (typeName === 'valChange') {
            reactionsMap[path].fns.push(fn);
          } else {
            const [type, name] = typeName.split('/');
            if (!reactionsMap[path][type][name]) {
              reactionsMap[path][type][name] = [fn];
            } else {
              reactionsMap[path][type][name].push(fn);
            }
          }
        };
        const resolveReaction = (crtInsPath, targetPath, reaction) => () => {
          const { instance: crtInstance } = widgetTree.default.widgetMap[crtInsPath] || {};
          const { instance: operateInstance } = widgetTree.default.widgetMap[targetPath] || {};
          let fullfill = true;
          const deps = [];
          if (reaction.source) {
            const sources = Array.isArray(reaction.source) ? reaction.source : [reaction.source];
            sources.forEach((item) => {
              const { instance } = widgetTree.default.widgetMap[parsePath(item, crtInsPath)];
              deps.push(instance);
            });
          }
          if (typeof reaction.if === 'string') {
            fullfill = (0, expression/* executeExpression */.Jq)(reaction.if, crtInstance, deps);
          }
          const operations = fullfill ? reaction.then : reaction.else;
          executeOperations(operations, operateInstance, deps);
        };
        const executeOperations = (operations, instance, deps) => {
          if (operations) {
            if (operations.state) {
              Object.keys(operations.state).forEach((key) => {
                let val = operations.state[key];
                if (typeof val === 'string' && /^{{.+}}$/.test(val.trim())) {
                  val = (0, expression/* executeExpression */.Jq)(val, instance, deps);
                }
                instance.setState(key, val);
              });
            }
            ;
            if (Array.isArray(operations.actions)) {
              operations.actions.forEach((item) => {
                (0, expression/* executeExpression */.Jq)(item, instance, deps);
              });
            }
          }
          ;
        };
        const parsePath = (path, instance) => ((0, expression/* isExpression */.UT)(path) ? (0, expression/* executeExpression */.Jq)(path, instance) : path);
        const reactionRegister = (path, reactions = []) => {
          const { instance } = widgetTree.default.widgetMap[path] || {};
          if (reactions && Array.isArray(reactions)) {
            reactions.forEach((reaction) => {
              const subscribePaths = reaction.source ? Array.isArray(reaction.source) ? reaction.source : [reaction.source] : [path];
              const targePath = parsePath(typeof reaction.target === 'string' ? reaction.target : path, instance);
              subscribePaths.forEach((p) => {
                const sourcePathItem = parsePath(p, instance);
                if (typeof reaction.lifetime === 'string') {
                  subscribe(sourcePathItem, `lifetime/${reaction.lifetime}`, resolveReaction(path, targePath, reaction));
                }
                if (typeof reaction.effect === 'string') {
                  subscribe(sourcePathItem, `effect/${reaction.effect}`, resolveReaction(path, targePath, reaction));
                }
                if (!reaction.lifetime && !reaction.effect) {
                  subscribe(sourcePathItem, 'valChange', resolveReaction(path, targePath, reaction));
                }
              });
            });
          }
        };
        const reactionUnRegister = (path) => {
          delete reactionsMap[path];
        };
        const reactionDispatch = (path, typeName) => {
          let _a; let _b;
          const [type = '', name = ''] = typeName.split('/');
          let fns = [];
          if (reactionsMap[path]) {
            if (type === 'valChange') {
              fns = reactionsMap[path].fns;
            } else if ((_b = (_a = reactionsMap[path]) == null ? void 0 : _a[type]) == null ? void 0 : _b[name]) {
              fns = reactionsMap[path][type][name];
            }
            fns.forEach((fn) => {
              fn();
            });
          }
        };

        // EXTERNAL MODULE: ./src/core/validator.ts
        const validator = __webpack_require__(1837);
        // EXTERNAL MODULE: ./src/core/events.ts
        const events = __webpack_require__(3660);
        // EXTERNAL MODULE: ./src/util/fetch.ts
        const fetch = __webpack_require__(374);
        ;// CONCATENATED MODULE: ./src/adapter/widget/Widget.ts

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
        const __objRest = (source, exclude) => {
          const target = {};
          for (var prop in source) if (__hasOwnProp.call(source, prop) && exclude.indexOf(prop) < 0) target[prop] = source[prop];
          if (source != null && __getOwnPropSymbols) for (var prop of __getOwnPropSymbols(source)) {
            if (exclude.indexOf(prop) < 0 && __propIsEnum.call(source, prop)) target[prop] = source[prop];
          }
          return target;
        };
        const __async = (__this, __arguments, generator) => new Promise((resolve, reject) => {
          const fulfilled = (value) => {
            try {
              step(generator.next(value));
            } catch (e) {
              reject(e);
            }
          };
          const rejected = (value) => {
            try {
              step(generator.throw(value));
            } catch (e) {
              reject(e);
            }
          };
          var step = x => (x.done ? resolve(x.value) : Promise.resolve(x.value).then(fulfilled, rejected));
          step((generator = generator.apply(__this, __arguments)).next());
        });


        /* harmony default export */ var Widget = ((0, external_vue_.defineComponent)({
          name: 'Widget',
          inheritAttrs: false,
          props: FieldProps.default,
          data() {
            return {
              loading: false,
              datasource: schema.default.resolveDefaultDatasource(this.schema),
              formItemProps: {
                tips: '',
              },
              state: {
                visible: this.visible,
                disabled: this.disabled,
                readonly: this.readonly,
                error: this.error,
              },
              errorTips: '',
              privateSchema: {},
              // 内部schema数据，请用setSchema和getSchema读取和设置
              key: '',
            };
          },
          computed: {
            widgetMap() {
              return widgetTree.default.widgetMap;
            },
            widgetNode() {
              return widgetTree.default.widgetMap[this.path];
            },
            parent() {
              let _a;
              return (_a = this.widgetNode) == null ? void 0 : _a.parent;
            },
            // 当前widget schema数据
            widgetSchema() {
              return (0, util.mergeDeep)({}, this.schema, this.privateSchema);
            },
          },
          watch: {
            modelValue: {
              handler(newValue, oldValue) {
                if (!(0, util.deepEquals)(newValue, oldValue)) {
                  setTimeout(() => {
                    reactionDispatch(this.path, 'valChange');
                    (0, validator.dispatchValidate)(this.path);
                  }, 0);
                }
              },
            },
            widgetSchema: {
              deep: true,
              handler(newValue, oldValue) {
                if ((0, util.deepEquals)(newValue, oldValue)) return;
                this.resetDatasource();
                this.key = (/* @__PURE__ */ new Date()).getTime()
                  .toString();
              },
            },
          },
          created() {
            const uiOptions = schema.default.getUiOptions(this.widgetSchema);
            this.formItemProps = __spreadProps(__spreadValues({}, uiOptions), {
              // schema配置不存在title时默认用属性名作为title
              label: uiOptions.showTitle ? uiOptions.label || core_path.default.getPathLastProp(this.path) : '',
              required: this.required,
            });
            const vNodeData = schema.default.getUiComponent(this.widgetSchema);
            const defaultProps = Object.assign({}, this.formItemProps, vNodeData || {});
            Object.keys(defaultProps).forEach((key) => {
              if (Reflect.has(this.state, key)) {
                this.setState(key, defaultProps[key]);
              }
            });
            widgetTree.default.addWidgetNode(this.path, this, 'node');
          },
          mounted() {
            reactionRegister(this.path, this.widgetSchema['ui:reactions']);
            reactionDispatch(this.path, 'valChange');
            reactionDispatch(this.path, 'lifetime/init');
          },
          beforeUnmount() {
            widgetTree.default.removeWidgetNode(this.path, this);
            reactionUnRegister(this.path);
          },
          methods: {
            setState(key, value) {
              if (Reflect.has(this.state, key)) {
                this.state[key] = value;
              } else if (key === 'value') {
                this.$emit('update:modelValue', { path: this.path, value });
              } else {
                console.warn(`Widget unsupported ${key} state, please check`);
              }
            },
            loadDataSource() {
              return __async(this, null, function* () {
                let _a; let _b;
                const xhrConfig = (_b = (_a = this.widgetSchema) == null ? void 0 : _a['ui:component']) == null ? void 0 : _b.remoteConfig;
                if (xhrConfig) {
                  const _c = xhrConfig; const { url, params } = _c; const reset = __objRest(_c, ['url', 'params']);
                  const { request: http = fetch/* default */.Z, responseParse } = this.httpAdapter;
                  try {
                    this.loading = true;
                    const remoteURL = (0, expression/* executeExpression */.Jq)(url, this);
                    const requestParams = (0, util.isObj)(params) ? (0, expression/* executeExpression */.Jq)(params, this) : params;
                    this.datasource = yield http(remoteURL, __spreadProps(__spreadValues({}, reset), {
                      params: requestParams,
                      responseParse,
                    }));
                    this.loading = false;
                  } catch (e) {
                    this.loading = false;
                    console.error(e);
                  }
                }
              });
            },
            setErrorTips(tips) {
              this.errorTips = tips;
            },
            getValue(path) {
              return core_path.default.getPathVal(this.rootData, path);
            },
            getReadonlyValue() {
              let _a; let _b;
              let val = this.modelValue;
              if (((_a = this.widgetSchema['ui:component']) == null ? void 0 : _a.type) === 'password') {
                val = '******';
              } else if (this.datasource) {
                const item = (_b = this.datasource) == null ? void 0 : _b.find(item2 => item2.value === this.modelValue);
                if (item) {
                  val = item.label;
                }
              }
              let value = val === '' ? '--' : val;
              if (Object.prototype.toString.call(value) === '[Object Object]') {
                value = JSON.stringify(value);
              } else if (Array.isArray(value)) {
                const isTrue = value.some(item => item && typeof item === 'object');
                if (isTrue) {
                  value = JSON.stringify(value);
                } else {
                  value = value.join(',');
                }
              } else {
                value = String(value);
              }
              return value;
            },
            getSchema() {
              return this.widgetSchema;
            },
            setSchema(data) {
              try {
                this.privateSchema = JSON.parse(JSON.stringify(data));
              } catch (err) {
                console.warn(err);
              }
              return this.widgetSchema;
            },
            resetDatasource() {
              let _a; let _b;
              const xhrConfig = (_b = (_a = this.widgetSchema) == null ? void 0 : _a['ui:component']) == null ? void 0 : _b.remoteConfig;
              if (xhrConfig) {
                this.loadDataSource();
              } else {
                this.datasource = schema.default.resolveDefaultDatasource(this.widgetSchema);
              }
            },
          },
          render() {
            let _b; let _c; let _d; let _e;
            const _a = schema.default.getUiComponent(this.widgetSchema); const { name } = _a; const uiVnodeData = __objRest(_a, ['name']);
            const widgetProps = __spreadProps(__spreadValues({}, this.$props), {
              // 透传field全部属性给widget，widget控件自行处理特殊逻辑
              loading: this.loading,
              modelValue: this.modelValue,
            });
            const self = this;
            const widgetName = register.default.getComponent(name) || name || schema.default.getDefaultWidget(this.widgetSchema);
            const widgetEvents = ((_b = events/* default */.Z.callbacks) == null ? void 0 : _b[this.path]) || {};
            const renderFormItem = () => {
              let _a2;
              return this.state.readonly && this.readonlyMode === 'value' && ((_a2 = this.widgetSchema['ui:component']) == null ? void 0 : _a2.name) !== 'table' ? renderReadonlyWidget : renderWidget;
            };
            const renderWidget = (_e = (_d = (_c = this.$slots).default) == null ? void 0 : _d.call(_c, { path: this.path })) != null ? _e : (0, external_vue_.h)(
              widgetName,
              (0, util.mergeDeep)(
                __spreadProps(__spreadValues(__spreadValues(__spreadValues({}, widgetProps), uiVnodeData || {}), Object.keys(widgetEvents).reduce((pre, key) => {
                  pre[`on${(0, util.capitalizeFirstLetter)(key)}`] = widgetEvents[key];
                  return pre;
                }, {})), {
                  schema: this.widgetSchema,
                  class: {
                    pr20: this.removeable,
                  },
                  onClick() {
                    let _a2;
                    reactionDispatch(self.path, 'effect/click');
                    (_a2 = widgetEvents.click) == null ? void 0 : _a2.forEach(event => event());
                  },
                  'onUpdate:modelValue': (value) => {
                    let _a2;
                    self.$emit('update:modelValue', { path: self.path, value });
                    (_a2 = widgetEvents['update:modelValue']) == null ? void 0 : _a2.forEach(event => event());
                  },
                }),
                uiVnodeData,
                __spreadProps(__spreadValues({}, this.state), {
                  datasource: this.datasource,
                  readonly: this.readonly,
                  readonlyMode: this.readonlyMode,
                }),
              ),
            );
            const renderSuffix = () => {
              let _a2; let _b2;
              return (_b2 = (_a2 = this.$slots).suffix) == null ? void 0 : _b2.call(_a2, { path: this.path, schema: this.widgetSchema });
            };
            const renderReadonlyWidget = (0, external_vue_.h)('div', {}, { default: () => this.getReadonlyValue() });
            const renderDelete = () => {
              if (!this.removeable) return null;
              return (0, external_vue_.h)(
                'span',
                {
                  class: ['bk-schema-form-group-delete'],
                  style: {
                    right: '0px',
                    top: '0px',
                  },
                  onClick: () => {
                    self.$emit('remove', self.path);
                  },
                },
                {
                  default: () => (0, external_vue_.h)('i', {
                    class: ['bk-icon icon-close3-shape'],
                  }),
                },
              );
            };
            const renderError = () => (this.state.error ? (0, external_vue_.h)('p', {
              class: 'bk-schema-form-item__error-tips',
            }, { default: () => this.errorTips }) : null);
            const renderFormTips = () => (this.formItemProps.tips ? (0, external_vue_.h)('p', {
              class: ['mt5', 'mb0', 'f12'],
              style: {
                color: '#5e6d82',
                lineHeight: '1.5em',
              },
            }, { default: () => this.formItemProps.tips }) : null);
            return (0, external_vue_.h)(
              register.default.getBaseWidget('form-item'),
              __spreadProps(__spreadValues({
                key: this.key,
              }, this.formItemProps), {
                style: __spreadProps(__spreadValues(__spreadValues({}, this.layout.item || {}), this.layout.container || {}), {
                  // 表单项显示和隐藏状态
                  display: this.state.visible ? '' : 'none',
                }),
                class: {
                  'bk-schema-form-item--error': this.state.error,
                },
              }),
              {
                default: () => [
                  renderFormItem(),
                  renderSuffix(),
                  renderDelete(),
                  renderError(),
                  renderFormTips(),
                ],
              },
            );
          },
        }));
        /***/ }),

      /***/ 7213:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony import */ const _util_fetch__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(374);


        /* harmony default export */ __webpack_exports__.default = ({
          // 表单值
          modelValue: {
            type: Object,
            default: () => ({}),
          },
          rules: {
            type: Object,
            default: () => ({}),
          },
          schema: {
            type: Object,
            default: () => ({}),
          },
          width: {
            type: [String, Number],
            default: '100%',
          },
          // 表单布局
          layout: {
            type: [Array, Object],
            default: () => [],
          },
          // 表单类型
          formType: {
            type: String,
            default: 'default',
          },
          // 表单全局上下文
          context: {
            type: Object,
            default: () => ({}),
          },
          // http请求适配器
          httpAdapter: {
            type: Object,
            default: () => ({
              request: _util_fetch__WEBPACK_IMPORTED_MODULE_0__/* ["default"] */ .Z,
              // 请求方法
              responseParse: res => res,
              // fetch请求返回数据通用解析函数
              // responseParse: {
              //   dataKey: 'data',
              //   valueKey: 'value',
              //   labelKey: 'label',
              // }, // 也可以是对像形式
            }),
          },
          readonly: {
            type: Boolean,
            default: false,
          },
          readonlyMode: {
            type: String,
            default: 'value',
            validator: value => ['value', 'custom'].includes(value),
          },
          labelWidth: {
            type: Number,
            default: 150,
          },
        });
        /***/ }),

      /***/ 3660:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        /* unused harmony export FormEvent */

        const __defProp = Object.defineProperty;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __publicField = (obj, key, value) => {
          __defNormalProp(obj, typeof key !== 'symbol' ? `${key}` : key, value);
          return value;
        };
        class FormEvent {
          constructor() {
            __publicField(this, 'callbacks');
            this.callbacks = /* @__PURE__ */ Object.create(null);
          }
          on(path, type, cb) {
            if (!(path in this.callbacks)) {
              this.callbacks[path] = {};
            }
            if (!(type in this.callbacks[path])) {
              this.callbacks[path][type] = [];
            }
            this.callbacks[path][type].push(cb);
            return this;
          }
          off(path, type, cb) {
            if (!(path && type)) {
              this.callbacks = /* @__PURE__ */ Object.create(null);
            } else if (path && !type) {
              delete this.callbacks[path];
            } else if (path && type && !cb) {
              delete this.callbacks[path][type];
            } else {
              const events = this.callbacks[path][type];
              for (const index in events) {
                if (cb === events[index]) {
                  events.splice(Number(index), 1);
                }
              }
            }
            return this;
          }
          once(path, type, cb) {
            const _this = this;
            function innerOnce(...arg) {
              cb(...arg);
              _this.off(path, type, innerOnce);
            }
            innerOnce.fn = cb;
            this.on(path, type, innerOnce);
            return this;
          }
          emit(path, type, ...arg) {
            if (!this.callbacks[path]) return;
            if (type in this.callbacks[path]) {
              const runs = [...this.callbacks[path][type]];
              for (const cb of runs) {
                cb(...arg);
              }
            }
          }
        }
        /* harmony default export */ __webpack_exports__.Z = (new FormEvent());
        /***/ }),

      /***/ 8343:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        /* harmony export */ __webpack_require__.d(__webpack_exports__, {
          /* harmony export */   Jq() {
            return /* binding */ executeExpression;
          },
          /* harmony export */   UT() {
            return /* binding */ isExpression;
          },
          /* harmony export */ });
        /* unused harmony exports getContext, parseStrTemplate */
        /* harmony import */ const _util__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(1851);
        /* harmony import */ const _register__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(7859);


        const getContext = (instance2) => {
          const { context: context2, loadDataSource, validate, schema, rootData, widgetNode } = instance2;
          return {
            $self: instance2,
            $context: context2,
            $schema: schema,
            $rules: schema.rules,
            $loadDataSource: loadDataSource,
            $validate: validate,
            $rootData: rootData,
            $widgetNode: widgetNode,
          };
        };
        const executeExpression = (expression, instance, $dep = []) => {
          const {
            $self,
            $context,
            $schema,
            $rules,
            $loadDataSource,
            $validate,
            $rootData,
            $widgetNode,
          } = getContext(instance);
          const context = {
            $self,
            $context,
            $schema,
            $rules,
            $loadDataSource,
            $validate,
            $rootData,
            $widgetNode,
            $dep,
          };
          if (typeof expression === 'string') {
            if (!/^{{.+}}$/.test(expression.trim())) return expression;
            const expStr = expression.trim().replace(/(^{{)|(}}$)/g, '')
              .trim();
            const innerFuncs = ['$loadDataSource', '$validate'];
            const func = function ({
              $self,
              $context,
              $schema,
              $rules,
              $loadDataSource,
              $validate,
              $rootData,
              $widgetNode,
              $dep,
            }) {
              try {
                return innerFuncs.includes(expStr) ? eval(`${expStr}()`) : eval(expStr);
              } catch (err) {
                console.error(`execute ${expStr} error, please check. 
`, err);
              }
            };
            return func(context);
          }
          if ((0, _util__WEBPACK_IMPORTED_MODULE_0__.isObj)(expression)) {
            Object.keys(expression).forEach((key) => {
              expression[key] = executeExpression(expression[key], instance);
            });
            return expression;
          }
        };
        const parseStrTemplate = (expression2) => {
          const $context2 = _register__WEBPACK_IMPORTED_MODULE_1__.Registry.context;
          const expStr2 = expression2.trim().replace(/(^{{)|(}}$)/g, '')
            .trim();
          try {
            const func2 = new Function('$context', `return ${expStr2}`);
            return func2($context2);
          } catch (err) {
            console.error(`parse template ${expression2} error`, err);
          }
        };
        const isExpression = expression2 => typeof expression2 === 'string' && /{{.*}}/.test(expression2);
        /***/ }),

      /***/ 3570:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony export */ __webpack_require__.d(__webpack_exports__, {
          /* harmony export */   default() {
            return /* binding */ Layout;
          },
          /* harmony export */ });

        const __defProp = Object.defineProperty;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __publicField = (obj, key, value) => {
          __defNormalProp(obj, typeof key !== 'symbol' ? `${key}` : key, value);
          return value;
        };
        class Layout {
          constructor(layout = []) {
            __publicField(this, 'layout');
            if (Array.isArray(layout)) {
              this.layout = this.parseLayout({
                prop: '',
                group: layout,
              });
            } else {
              this.layout = this.parseLayout(layout);
            }
          }
          static findLayoutByProp(prop, layout) {
            let layoutConfig;
            layout.find((row) => {
              layoutConfig = row.find(col => col.prop === prop);
              return layoutConfig;
            });
            return layoutConfig;
          }
          transformValueToPixel(value) {
            if (typeof value === 'number') {
              return `${value}px`;
            }
            return value;
          }
          parseLayout(config) {
            const dim = this.getLayoutDimension(config.group);
            const gridTemplate = this.parseGridTemplate(dim);
            const group = (config.group || []).map((current) => {
              if (!Array.isArray(current)) {
                console.error(`layout ${JSON.stringify(current)} error, must be a array`);
                return [];
              }
              const parseCurrent = current.map((item) => {
                if (typeof item === 'string' || typeof item === 'number') {
                  return {
                    prop: item,
                    item: {
                      gridArea: item,
                      overflow: 'hidden',
                    },
                  };
                }
                if (typeof item === 'object' && Reflect.has(item, 'group')) {
                  return this.parseLayout(item);
                }
                return item;
              });
              return parseCurrent;
            });
            const gridTemplateAreas = this.parseGridTemplateAreas(dim, group);
            const layoutConfig = {
              prop: config.prop || '',
              item: __spreadValues({
                gridArea: config.prop,
                overflow: 'hidden',
              }, config.item),
              container: __spreadValues(__spreadValues({
                display: 'grid',
                gridTemplateAreas,
                gridGap: '20px',
              }, gridTemplate), config.container),
              group,
            };
            return layoutConfig;
          }
          getLayoutDimension(layout = []) {
            return layout.reduce((pre, current) => {
              if (!Array.isArray(current)) {
                console.error(`layout ${JSON.stringify(current)} error, must be a array`);
              }
              if (current) {
                pre.columns = Math.max(pre.columns, current.length || 0);
              }
              pre.rows += 1;
              return pre;
            }, {
              columns: 0,
              rows: 0,
            });
          }
          parseGridTemplate(dim) {
            return {
              gridTemplateColumns: this.repeatTemplate(dim.columns, false),
              gridTemplateRows: this.repeatTemplate(dim.rows),
            };
          }
          parseGridTemplateAreas(gridTemplate, group) {
            return group.reduce((area, rows) => {
              const newRows = this.autoFillColumns(rows, gridTemplate.columns);
              area.push(`"${newRows.join(' ')}"`);
              return area;
            }, []).join('\n');
          }
          // 当前列数不够时自动填充
          autoFillColumns(rows, maxColumns) {
            if (rows.length === maxColumns) {
              return rows.map(row => row.prop);
            }
            const fillLen = Math.floor((maxColumns - rows.length) / rows.length);
            const newRows = rows.reduce((pre, row) => {
              pre.push(row.prop);
              const fillData = new Array(fillLen).fill(row.prop);
              return pre.concat(fillData);
            }, []);
            if (newRows.length < maxColumns) {
              const remainData = new Array(maxColumns - newRows.length).fill('.');
              return newRows.concat(remainData);
            }
            return newRows;
          }
          repeatTemplate(len, auto = true) {
            return new Array(len + 1).join(auto ? 'auto ' : '1fr ')
              .trim();
          }
        }
        /***/ }),

      /***/ 4879:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony export */ __webpack_require__.d(__webpack_exports__, {
          /* harmony export */   default() {
            return /* binding */ Path;
          },
          /* harmony export */ });

        const __defProp = Object.defineProperty;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __publicField = (obj, key, value) => {
          __defNormalProp(obj, typeof key !== 'symbol' ? `${key}` : key, value);
          return value;
        };
        class Path {
          static getCurPath(parent, current) {
            return parent === '' ? current : [parent, current].join(this.separator);
          }
          static getPathVal(obj, path, leftDeviation = 0) {
            if (!path) return obj;
            const pathArr = path.split(this.separator);
            for (let i = 0; i < pathArr.length - leftDeviation; i += 1) {
              if (obj === void 0) return void 0;
              obj = pathArr[i] === '' ? obj : obj[pathArr[i]];
            }
            return obj;
          }
          static setPathValue(obj = {}, path, value) {
            const newValue = JSON.parse(JSON.stringify(obj));
            const pathArr = path.split(this.separator);
            const lastProp = pathArr.pop() || '';
            let target = newValue;
            pathArr.forEach((prop) => {
              if (!target[prop]) target[prop] = {};
              target = target[prop];
            });
            target[lastProp] = value;
            return newValue;
          }
          // 获取当前路径的字路径（相对于父路径）
          static getSubPath(parent, current) {
            return current.replace(`${parent}.`, '');
          }
          // 获取路径最后一个属性
          static getPathLastProp(path) {
            return path.split(this.separator).pop();
          }
          // 获取父路径
          static getParentPath(path) {
            const arrPath = path.split(this.separator);
            if (arrPath.length <= 1) {
              return '';
            }
            return arrPath.slice(0, arrPath.length - 1).join(this.separator);
          }
        }
        __publicField(Path, 'separator', '.');
        /***/ }),

      /***/ 4865:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony export */ __webpack_require__.d(__webpack_exports__, {
          /* harmony export */   default() {
            return /* binding */ createProxy;
          },
          /* harmony export */ });

        function createProxy(schema, context) {
          return new Proxy(schema, {
            get(target, key, receiver) {
              if (typeof target[key] === 'function') {
                return target[key].apply(context);
              }
              return Reflect.get(target, key, receiver);
            },
          });
        }
        /***/ }),

      /***/ 7859:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony export */ __webpack_require__.d(__webpack_exports__, {
          /* harmony export */   Registry() {
            return /* binding */ Registry;
          },
          /* harmony export */ });
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_0___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_0__);

        const __defProp = Object.defineProperty;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __publicField = (obj, key, value) => {
          __defNormalProp(obj, typeof key !== 'symbol' ? `${key}` : key, value);
          return value;
        };

        const _Registry = class _Registry {
          constructor() {
            // 基础类型控件
            __publicField(this, 'widgets', /* @__PURE__ */ new Map());
            // 自定义组件
            __publicField(this, 'components', /* @__PURE__ */ new Map());
            // 每种Schema type对于的处理器
            __publicField(this, 'fields', /* @__PURE__ */ new Map());
          }
          addComponentsMap(coms = {}) {
            this.addMap('components', coms);
          }
          getComponent(key) {
            return this.components.get(key);
          }
          addFieldsMap(map = {}) {
            this.addMap('fields', map);
          }
          getField(key) {
            return this.fields.get(key);
          }
          addBaseWidgets(widgets = {}) {
            this.addMap('widgets', widgets);
          }
          // 获取基础控件
          getBaseWidget(name) {
            if (this.widgets.has(name)) {
              return this.widgets.get(name);
            }
            if (name && name.indexOf(_Registry.namespace) !== 0) {
              return (0, vue__WEBPACK_IMPORTED_MODULE_0__.resolveComponent)(`${_Registry.namespace}-${name}`);
            }
            return (0, vue__WEBPACK_IMPORTED_MODULE_0__.resolveComponent)(name);
          }
          addMap(props, map) {
            if (!props || !map) return;
            Object.entries(map).forEach(([key, value]) => {
              if (this[props].has(key)) {
                console.warn('repeat key', key);
                return;
              }
              if (typeof value === 'string') {
                this[props].set(key, (0, vue__WEBPACK_IMPORTED_MODULE_0__.resolveComponent)(value));
              } else {
                this[props].set(key, value);
              }
            });
          }
        };
        // 全局命名空间
        __publicField(_Registry, 'namespace', 'bk');
        // 全局上下
        __publicField(_Registry, 'context', {});
        const Registry = _Registry;
        /* harmony default export */ __webpack_exports__.default = (new Registry());
        /***/ }),

      /***/ 8683:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony export */ __webpack_require__.d(__webpack_exports__, {
          /* harmony export */   default() {
            return /* binding */ Schema;
          },
          /* harmony export */ });
        /* harmony import */ const _util__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(1851);
        /* harmony import */ const _core_register__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(7859);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(748);
        /* harmony import */ const vue__WEBPACK_IMPORTED_MODULE_2___default = /* #__PURE__*/__webpack_require__.n(vue__WEBPACK_IMPORTED_MODULE_2__);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
        const __objRest = (source, exclude) => {
          const target = {};
          for (var prop in source) if (__hasOwnProp.call(source, prop) && exclude.indexOf(prop) < 0) target[prop] = source[prop];
          if (source != null && __getOwnPropSymbols) for (var prop of __getOwnPropSymbols(source)) {
            if (exclude.indexOf(prop) < 0 && __propIsEnum.call(source, prop)) target[prop] = source[prop];
          }
          return target;
        };
        const __publicField = (obj, key, value) => {
          __defNormalProp(obj, typeof key !== 'symbol' ? `${key}` : key, value);
          return value;
        };


        const _Schema = class _Schema {
          static resolveRef() {
          }
          static resolveDependencies() {
          }
          static resolveAdditionalProperties() {
          }
          static resolveSchema(schema) {
            if (!(0, _util__WEBPACK_IMPORTED_MODULE_0__.isObj)(schema)) return {};
            if ((0, _util__WEBPACK_IMPORTED_MODULE_0__.hasOwnProperty)(schema, 'allOf')) {
            }
            if ((0, _util__WEBPACK_IMPORTED_MODULE_0__.hasOwnProperty)(schema, '$ref')) {
            }
            return schema;
          }
          // 获取Schema字段默认值
          static getSchemaDefaultValue(_schema) {
            const schema = (0, _util__WEBPACK_IMPORTED_MODULE_0__.isObj)(_schema) ? _schema : {};
            switch (this.getSchemaType(schema)) {
              case 'null':
                return null;
              case 'object':
                return Object.keys(schema.properties || {}).reduce((pre, key) => {
                  let _a;
                  const defaultValue = this.getSchemaDefaultValue((_a = schema.properties) == null ? void 0 : _a[key]);
                  pre[key] = defaultValue;
                  return pre;
                }, {});
              case 'array':
                if (schema.default && Array.isArray(schema.default)) {
                  return schema.default;
                }
                return Array.isArray(schema.items) ? schema.items.map(item => this.getSchemaDefaultValue(item)) : [];
            }
            return schema.default !== void 0 ? schema.default : (0, _util__WEBPACK_IMPORTED_MODULE_0__.initializationValue)(schema.type || 'any');
          }
          static getSchemaType(schema) {
            const { type } = schema;
            if (!type && schema.const) {
              return (0, _util__WEBPACK_IMPORTED_MODULE_0__.valueType)(schema.const);
            }
            if (!type && schema.enum) {
              return 'string';
            }
            if (!type && schema.items) {
              return 'array';
            }
            return type;
          }
          static getUiProps(props, schema) {
            if (!props || !props.startsWith('ui:')) {
              console.warn('ui props must start with ui:');
            }
            return schema[props] || {};
          }
          static getSchemaField(schema) {
            let _a; let _b;
            const field = schema['ui:field'];
            if (field) {
              return field;
            }
            if ((_a = schema.oneOf) == null ? void 0 : _a.length) {
              return {
                name: _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getField('composition'),
                composition: 'oneOf',
              };
            }
            if ((_b = schema.anyOf) == null ? void 0 : _b.length) {
              return {
                name: _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getField('composition'),
                composition: 'anyOf',
              };
            }
            const defaultField = _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getField(this.getSchemaType(schema));
            if (defaultField) {
              return {
                name: defaultField,
              };
            }
            return {
              name: null,
            };
          }
          static isMultiSelect(schema) {
            if (!schema.uniqueItems || !schema.items) {
              return false;
            }
            return Array.isArray(schema.items.enum);
          }
          static isTupleArray(schema) {
            let _a;
            return Array.isArray(schema.items) && ((_a = schema.items) == null ? void 0 : _a.length) > 0 && schema.items.every(item => (0, _util__WEBPACK_IMPORTED_MODULE_0__.isObj)(item));
          }
          // 是否是自定义数组类型控件（如：label）
          static isCustomArrayWidget(schema) {
            let _a;
            const com = (_a = schema['ui:component']) == null ? void 0 : _a.name;
            return schema.type === 'array' && com;
          }
          static resolveFormComponent(com) {
            if (typeof com === 'string' && com) {
              return (0, vue__WEBPACK_IMPORTED_MODULE_2__.resolveComponent)(com);
            }
            return com;
          }
          static getGroupWrap(schema) {
            const _a = schema['ui:group'] || {}; const { name } = _a; const groupVnode = __objRest(_a, ['name']);
            return __spreadProps(__spreadValues({}, groupVnode), {
              name: this.resolveFormComponent(_core_register__WEBPACK_IMPORTED_MODULE_1__.default.getComponent(name) || name || _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getComponent('group')),
            });
          }
          static getUiComponent(schema) {
            const _a = schema['ui:component'] || {}; const { name } = _a; const vnodeData = __objRest(_a, ['name']);
            return __spreadValues({
              name: this.resolveFormComponent(_core_register__WEBPACK_IMPORTED_MODULE_1__.default.getComponent(name) || name),
            }, vnodeData);
          }
          static getDefaultWidget(schema) {
            let _a; let _b; let _c; let _d;
            const type = this.getSchemaType(schema);
            let defaultComponent = null;
            if (type === 'string' && Array.isArray(schema.enum)) {
              defaultComponent = _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getComponent('select');
            }
            if (type === 'array' && _Schema.isMultiSelect(schema)) {
              defaultComponent = _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getComponent('checkbox');
            }
            if (typeof type !== 'object' && (((_a = schema.oneOf) == null ? void 0 : _a.length) && ((_b = schema.oneOf) == null ? void 0 : _b.every(item => item.const)) || ((_c = schema.anyOf) == null ? void 0 : _c.length) && ((_d = schema.anyOf) == null ? void 0 : _d.every(item => item.const)))) {
              defaultComponent = _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getComponent('select');
            }
            if (defaultComponent) {
              return defaultComponent;
            }
            const typeComponentMap = {
              string: 'input',
              number: 'input',
              integer: 'input',
              boolean: 'switcher',
              null: '',
            };
            const name = typeComponentMap[type];
            const defaultWidget = _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getComponent(name) || _core_register__WEBPACK_IMPORTED_MODULE_1__.default.getBaseWidget(name);
            if (defaultWidget) {
              return defaultWidget;
            }
            console.warn(`\u672A\u6CE8\u518C\u7C7B\u578B${type}\u5BF9\u5E94\u7684\u9ED8\u8BA4\u8868\u5355\u9879`);
            return null;
          }
          static isRequired(schema, name) {
            return Array.isArray(schema.required) && schema.required.includes(name);
          }
          static getUiOptions(schema) {
            const options = __spreadValues({
              showTitle: true,
              label: schema.title,
              desc: schema.description,
              minLength: schema.minLength,
              maxLength: schema.maxLength,
            }, schema['ui:props'] || {});
            return __spreadProps(__spreadValues({}, options), {
              // 0.1 兼容formItem设置 labelWidth 0 不生效问题
              labelWidth: options.showTitle ? options.labelWidth : 0.1,
            });
          }
          // 当前属性是否被依赖
          static getDependencies(schema, name) {
            return Object.entries(schema.dependencies || {}).find(data => Array.isArray(data[1]) && data[1].includes(name));
          }
          static resolveDefaultDatasource(schema) {
            let _a; let _b;
            if ((_a = schema['ui:component']) == null ? void 0 : _a.datasource) {
              return schema['ui:component'].datasource;
            }
            if (Array.isArray(schema.enum)) {
              const data = schema.enum;
              return data.map(value => ({ value, label: value }));
            }
            if (Array.isArray((_b = schema.items) == null ? void 0 : _b.enum)) {
              const data = schema.items.enum || [];
              return data.map(value => ({ value, label: value }));
            }
            if (typeof schema.type !== 'object' && schema.oneOf && schema.oneOf.every(item => item.const)) {
              const data = schema.oneOf.map(item => ({ value: item.const, label: item.title || item.const }));
              return data;
            }
            if (typeof schema.type !== 'object' && schema.anyOf && schema.anyOf.every(item => item.const)) {
              const data = schema.anyOf.map(item => ({ value: item.const, label: item.title || item.const }));
              return data;
            }
          }
          constructor(rootSchema) {
            _Schema.rootSchema = rootSchema;
          }
        };
        __publicField(_Schema, 'rootSchema');
        const Schema = _Schema;
        /***/ }),

      /***/ 1837:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony export */ __webpack_require__.d(__webpack_exports__, {
          /* harmony export */   DEFAULT_RULES() {
            return /* binding */ DEFAULT_RULES;
          },
          /* harmony export */   ajv() {
            return /* binding */ ajv;
          },
          /* harmony export */   dispatchValidate() {
            return /* binding */ dispatchValidate;
          },
          /* harmony export */   registryGlobalRules() {
            return /* binding */ registryGlobalRules;
          },
          /* harmony export */   setWidgetErrorTips() {
            return /* binding */ setWidgetErrorTips;
          },
          /* harmony export */   validateForm() {
            return /* binding */ validateForm;
          },
          /* harmony export */   validateFormItem() {
            return /* binding */ validateFormItem;
          },
          /* harmony export */   validateFormWithResult() {
            return /* binding */ validateFormWithResult;
          },
          /* harmony export */   validateSchema() {
            return /* binding */ validateSchema;
          },
          /* harmony export */ });
        /* harmony import */ const _util__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(1851);
        /* harmony import */ const _expression__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(8343);
        /* harmony import */ const ajv__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(1581);
        /* harmony import */ const ajv__WEBPACK_IMPORTED_MODULE_2___default = /* #__PURE__*/__webpack_require__.n(ajv__WEBPACK_IMPORTED_MODULE_2__);
        /* harmony import */ const ajv_formats__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(5477);
        /* harmony import */ const ajv_formats__WEBPACK_IMPORTED_MODULE_3___default = /* #__PURE__*/__webpack_require__.n(ajv_formats__WEBPACK_IMPORTED_MODULE_3__);
        /* harmony import */ const ajv_i18n_localize_zh__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(6366);
        /* harmony import */ const ajv_i18n_localize_zh__WEBPACK_IMPORTED_MODULE_4___default = /* #__PURE__*/__webpack_require__.n(ajv_i18n_localize_zh__WEBPACK_IMPORTED_MODULE_4__);
        /* harmony import */ const _core_widgetTree__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(7564);

        const __async = (__this, __arguments, generator) => new Promise((resolve, reject) => {
          const fulfilled = (value) => {
            try {
              step(generator.next(value));
            } catch (e) {
              reject(e);
            }
          };
          const rejected = (value) => {
            try {
              step(generator.throw(value));
            } catch (e) {
              reject(e);
            }
          };
          var step = x => (x.done ? resolve(x.value) : Promise.resolve(x.value).then(fulfilled, rejected));
          step((generator = generator.apply(__this, __arguments)).next());
        });


        const ajv = new (ajv__WEBPACK_IMPORTED_MODULE_2___default())({
          strict: false,
        });
        ajv_formats__WEBPACK_IMPORTED_MODULE_3___default()(ajv);
        const VALIDATOR = 'validator';
        const OWN_RULE_PROPERTY = 'ui:rules';
        const DEBUG_PREFIX = '[bk-schema-form-validator]';
        const DEFAULT_RULES = {
          required: {
            message: '\u5FC5\u586B\u9879',
            validator: '{{ $self.value !== \'\' }}',
          },
        };
        const throwErr = (err) => {
          throw new Error(`${DEBUG_PREFIX} ${err}`);
        };
        const globalRules = /* @__PURE__ */ new Map();
        const registryGlobalRules = (rules) => {
          try {
            if (!rules) return;
            if ((rules == null ? void 0 : rules.constructor) !== Object) throwErr('global rules must be an object');
            Object.keys(rules).forEach((ruleName) => {
              const rule2 = rules[ruleName];
              if (!(0, _util__WEBPACK_IMPORTED_MODULE_0__.hasOwnProperty)(rule2, VALIDATOR)) throwErr(`'${ruleName}' rule must have a validator property`);
              const validator2 = rule2[VALIDATOR];
              if (!((0, _expression__WEBPACK_IMPORTED_MODULE_1__/* .isExpression */ .UT)(validator2) || (0, _util__WEBPACK_IMPORTED_MODULE_0__.isRegExp)(validator2) || (validator2 == null ? void 0 : validator2.constructor) === Function)) throwErr(`'${ruleName}' must be one of expression or regexp or function`);
              globalRules.set(ruleName, rule2);
            });
          } catch (error) {
            throwErr(error);
          }
        };
        const validate = (rule, instance) => {
          let theRule = rule;
          if (typeof rule === 'string') {
            theRule = globalRules.get(rule);
            if (!theRule) throwErr(`'${rule} is not a valid global rule, you can registry it to global rules node or use form item own custom rules`);
          }
          const { validator, message } = theRule;
          let valid = true;
          if ((0, _expression__WEBPACK_IMPORTED_MODULE_1__/* .isExpression */ .UT)(validator)) {
            valid = (0, _expression__WEBPACK_IMPORTED_MODULE_1__/* .executeExpression */ .Jq)(validator, instance);
          } else if (typeof validator === 'function') {
            valid = validator(instance);
          } else if (eval(validator) instanceof RegExp) {
            valid = new RegExp(eval(validator)).test(instance.value);
          }
          return {
            valid,
            message,
          };
        };
        const setWidgetErrorTips = (path, isError, errorMsg) => {
          const formItem = _core_widgetTree__WEBPACK_IMPORTED_MODULE_5__.default.widgetMap[path];
          const { instance: instance2 } = formItem;
          if (formItem.type === 'node') {
            instance2 == null ? void 0 : instance2.setState('error', true);
            instance2 == null ? void 0 : instance2.setErrorTips(errorMsg);
          }
          const widgetPaths = path.split('.');
          const fieldTitleBreadcrumb = [];
          widgetPaths.forEach((thePath, thePathIndex) => {
            let _a;
            const currentPaths = widgetPaths.slice(0, widgetPaths.length - thePathIndex);
            const widgetPath = currentPaths.join('.');
            const theWidget = _core_widgetTree__WEBPACK_IMPORTED_MODULE_5__.default.widgetMap[widgetPath];
            const isIndex = theWidget.instance.schema.type === 'array' || !theWidget.instance.schema.title;
            fieldTitleBreadcrumb.push(isIndex ? currentPaths.pop() : theWidget.instance.schema.title);
            if (((_a = theWidget.instance) == null ? void 0 : _a.verifiable) && theWidget.type === 'group') {
              if (isError) {
                const groupErrors = `${fieldTitleBreadcrumb.reverse().join('-')}: ${errorMsg}`;
                theWidget.instance.setGroupErrorTips(path, groupErrors);
              } else {
                theWidget.instance.removeGroupErrorTips(path);
              }
            }
          });
        };
        const validateFormItem = (path) => {
          let _a;
          const formItem = _core_widgetTree__WEBPACK_IMPORTED_MODULE_5__.default.widgetMap[path];
          if (!formItem) return {
            result: true,
            message: '',
            path: '',
          };
          const { instance: instance2 } = formItem;
          if (formItem.type === 'group') {
            instance2 == null ? void 0 : instance2.clearGroupErrorTips();
          } else {
            instance2 == null ? void 0 : instance2.setState('error', false);
            instance2 == null ? void 0 : instance2.setErrorTips('');
            const widgetPaths = path.split('.');
            widgetPaths.forEach((thePath, thePathIndex) => {
              let _a2;
              const currentPaths = widgetPaths.slice(0, widgetPaths.length - thePathIndex).join('.');
              const theWidget = _core_widgetTree__WEBPACK_IMPORTED_MODULE_5__.default.widgetMap[currentPaths];
              if (((_a2 = theWidget.instance) == null ? void 0 : _a2.verifiable) && theWidget.type === 'group') {
                theWidget.instance.removeGroupErrorTips(path);
              }
            });
          }
          const ownSchema = instance2.schema;
          const schemaValidate = ajv.compile(ownSchema);
          const value = instance2.value === void 0 ? (0, _util__WEBPACK_IMPORTED_MODULE_0__.initializationValue)(ownSchema.type, {
            integer: 0,
            number: 0,
          }) : instance2.value;
          const schemaValid = schemaValidate(value);
          if (!schemaValid) {
            ajv_i18n_localize_zh__WEBPACK_IMPORTED_MODULE_4___default()(schemaValidate.errors);
            const errorsText = ajv.errorsText(schemaValidate.errors, { separator: '\n' });
            setWidgetErrorTips(path, true, errorsText);
            return {
              result: false,
              message: errorsText,
              path,
            };
          }
          const customRules = ((_a = instance2.schema) == null ? void 0 : _a[OWN_RULE_PROPERTY]) || [];
          let isError = false;
          let errorMsg = '';
          for (const rule2 of customRules) {
            const result = validate(rule2, instance2);
            if (!result.valid) {
              isError = true;
              errorMsg = result.message;
              break;
            }
          }
          if (isError) {
            setWidgetErrorTips(path, true, errorMsg);
            return {
              result: false,
              message: errorMsg,
              path,
            };
          }
          return {
            result: true,
            message: errorMsg,
            path,
          };
        };
        const validateForm = () => {
          let isValid = true;
          Object.keys(_core_widgetTree__WEBPACK_IMPORTED_MODULE_5__.default.widgetMap).forEach((path) => {
            let _a;
            if (!((_a = validateFormItem(path)) == null ? void 0 : _a.result)) isValid = false;
          });
          return isValid;
        };
        const validateFormWithResult = () => new Promise((resolve, reject) => {
          const result = Object.keys(_core_widgetTree__WEBPACK_IMPORTED_MODULE_5__.default.widgetMap).filter((path) => {
            let _a;
            return ((_a = _core_widgetTree__WEBPACK_IMPORTED_MODULE_5__.default.widgetMap[path]) == null ? void 0 : _a.type) === 'node';
          })
            .reduce((pre, path) => {
              const validateResult = validateFormItem(path);
              if (!(validateResult == null ? void 0 : validateResult.result)) {
                pre.push(validateResult);
              }
              return pre;
            }, []);
          if (result.length) {
            reject(result);
          } else {
            resolve([]);
          }
        });
        const validateSchema = schema => __async(void 0, null, function* () {
          try {
            return yield ajv.validateSchema(schema, true);
          } catch (err) {
            console.error('Schema\u4E0D\u7B26\u5408\u89C4\u8303, \u8BF7\u68C0\u67E5', err);
            return false;
          }
        });
        const dispatchValidate = path => validateFormItem(path);
        /***/ }),

      /***/ 7564:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony export */ __webpack_require__.d(__webpack_exports__, {
          /* harmony export */   WidgetNode() {
            return /* binding */ WidgetNode;
          },
          /* harmony export */   WidgetTree() {
            return /* binding */ WidgetTree;
          },
          /* harmony export */ });
        /* harmony import */ const _path__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(4879);

        const __defProp = Object.defineProperty;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __publicField = (obj, key, value) => {
          __defNormalProp(obj, typeof key !== 'symbol' ? `${key}` : key, value);
          return value;
        };

        class WidgetNode {
          constructor(config) {
            __publicField(this, 'id');
            __publicField(this, 'instance');
            __publicField(this, 'parent');
            __publicField(this, 'type');
            __publicField(this, 'index');
            // todo
            __publicField(this, 'children');
            const { id, instance, parent, index, type, children = [] } = config;
            this.id = id;
            this.type = type;
            this.index = index;
            this.instance = instance;
            this.parent = parent;
            this.children = children;
          }
          // 当前node的值
          get value() {
            let _a;
            return (_a = this.instance) == null ? void 0 : _a.value;
          }
          // 是否含有可见子节点
          get isChildrenVisible() {
            let _a;
            if (this.type === 'node') {
              return (_a = this.instance) == null ? void 0 : _a.state.visible;
            }
            return this.children.some(child => child.isChildrenVisible);
          }
          /**
   * 获取 parents
   */
          get parents() {
            if (!this.parent) {
              return [];
            }
            return [...this.parent.parents, this.parent];
          }
          // 第一个子节点
          get firstChild() {
            return this.children[0] || null;
          }
          // 最后一个子节点
          get lastChild() {
            return this.children[this.children.length - 1] || null;
          }
          // 指定属性下的同胞节点
          getSibling(lastProp) {
            let _a;
            const reg = new RegExp(`${_path__WEBPACK_IMPORTED_MODULE_0__.default.getPathLastProp(this.id) || ''}$`);
            const id = this.id.replace(reg, lastProp);
            return (_a = this.parent) == null ? void 0 : _a.children.find(node => node.id === id);
          }
          // 获取所以同胞节点（不含自己）
          getSiblings() {
            let _a;
            return ((_a = this.parent) == null ? void 0 : _a.children.filter(node => node.instance !== this.instance)) || [];
          }
          /**
   * 是否是叶子节点
   */
          get isLeaf() {
            return !this.children.length;
          }
          appendChild(node) {
            const nodes = Array.isArray(node) ? node : [node];
            const offset = node.index !== void 0 ? node.index : this.children.length;
            this.children.splice(offset, 0, ...nodes);
            this.children.slice(offset).forEach((node2, index) => {
              node2.index = offset + index;
            });
            return nodes;
          }
          removeChild(node) {
            const nodes = Array.isArray(node) ? node : [node];
            const removedChildIndex = [];
            nodes.forEach((node2) => {
              const { index } = node2;
              removedChildIndex.push(index);
              this.children.splice(index, 1);
            });
            const minIndex = Math.min(...removedChildIndex);
            this.children.slice(minIndex).forEach((node2, index) => {
              node2.index = minIndex + index;
            });
            return nodes;
          }
        }
        class WidgetTree {
          constructor() {
            __publicField(this, 'widgetMap', {});
          }
          addWidgetNode(path, instance, type, index) {
            if (path === '') {
              const node = new WidgetNode({
                id: '',
                type,
                index,
                parent: null,
                instance,
                children: [],
              });
              this.widgetMap[path] = node;
            } else {
              const parentId = _path__WEBPACK_IMPORTED_MODULE_0__.default.getParentPath(path);
              const parentNode = this.widgetMap[parentId];
              const node = new WidgetNode({
                id: (instance == null ? void 0 : instance.path) || path,
                type,
                index,
                parent: parentNode,
                instance,
                children: [],
              });
              if (!parentNode) {
                console.warn('Unexpected parent id, please check widget node', node);
              } else {
                parentNode.appendChild(node);
              }
              this.widgetMap[path] = node;
            }
          }
          removeWidgetNode(path, instance) {
            const node = this.widgetMap[path];
            if (node) {
              if (node.parent) {
                const { children } = node.parent;
                const index = children.findIndex(item => item.instance === instance);
                if (index > -1) {
                  children.splice(index, 1);
                  children.slice(index).forEach((node2, i) => {
                    node2.index = index + i;
                  });
                }
              }
              if (node.instance === instance) {
                delete this.widgetMap[path];
              }
            }
          }
        }
        /* harmony default export */ __webpack_exports__.default = (new WidgetTree());
        /***/ }),

      /***/ 374:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        /* harmony import */ const ___WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(1851);

        const __defProp = Object.defineProperty;
        const __defProps = Object.defineProperties;
        const __getOwnPropDescs = Object.getOwnPropertyDescriptors;
        const __getOwnPropSymbols = Object.getOwnPropertySymbols;
        const __hasOwnProp = Object.prototype.hasOwnProperty;
        const __propIsEnum = Object.prototype.propertyIsEnumerable;
        const __defNormalProp = (obj, key, value) => (key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value);
        const __spreadValues = (a, b) => {
          for (var prop in b || (b = {})) if (__hasOwnProp.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          if (__getOwnPropSymbols) for (var prop of __getOwnPropSymbols(b)) {
            if (__propIsEnum.call(b, prop)) __defNormalProp(a, prop, b[prop]);
          }
          return a;
        };
        const __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
        const __objRest = (source, exclude) => {
          const target = {};
          for (var prop in source) if (__hasOwnProp.call(source, prop) && exclude.indexOf(prop) < 0) target[prop] = source[prop];
          if (source != null && __getOwnPropSymbols) for (var prop of __getOwnPropSymbols(source)) {
            if (exclude.indexOf(prop) < 0 && __propIsEnum.call(source, prop)) target[prop] = source[prop];
          }
          return target;
        };
        const __async = (__this, __arguments, generator) => new Promise((resolve, reject) => {
          const fulfilled = (value) => {
            try {
              step(generator.next(value));
            } catch (e) {
              reject(e);
            }
          };
          const rejected = (value) => {
            try {
              step(generator.throw(value));
            } catch (e) {
              reject(e);
            }
          };
          var step = x => (x.done ? resolve(x.value) : Promise.resolve(x.value).then(fulfilled, rejected));
          step((generator = generator.apply(__this, __arguments)).next());
        });

        const methodsWithoutData = ['GET', 'HEAD', 'OPTIONS', 'DELETE'];
        const defaultConfig = {
          responseType: 'json',
          method: 'GET',
          params: {},
          headers: {},
          cache: 'no-cache',
        };
        /* harmony default export */ __webpack_exports__.Z = ((_0, ..._1) => __async(void 0, [_0, ..._1], function* (url, config = {}) {
          const _a = (0, ___WEBPACK_IMPORTED_MODULE_0__.mergeDeep)(defaultConfig, config); const {
            params,
            responseType = 'json',
            method = 'GET',
            headers = {},
            responseParse,
          } = _a; const reset = __objRest(_a, [
            'params',
            'responseType',
            'method',
            'headers',
            'responseParse',
          ]);
          let body;
          let requestURL = url;
          if (methodsWithoutData.includes(method.toUpperCase())) {
            requestURL = `${requestURL}?${(0, ___WEBPACK_IMPORTED_MODULE_0__.isObj)(params) ? new URLSearchParams(params) : params || ''}`;
          } else {
            if ((0, ___WEBPACK_IMPORTED_MODULE_0__.isObj)(params)) {
              headers['Content-Type'] = 'application/json;charset=utf-8';
              body = JSON.stringify(params);
            } else {
              body = params;
            }
          }
          try {
            const response = yield fetch(requestURL, __spreadProps(__spreadValues({}, reset), {
              method: method.toLocaleUpperCase(),
              headers,
              body,
            }));
            if (response.ok) {
              const res = yield response[responseType]();
              if (responseParse) {
                if (typeof responseParse === 'function') {
                  return Promise.resolve(responseParse(res));
                }
                if ((0, ___WEBPACK_IMPORTED_MODULE_0__.isObj)(responseParse)) {
                  const { dataKey = 'data', labelKey, valueKey } = responseParse;
                  const data = ((res == null ? void 0 : res[dataKey]) || []).map(item => __spreadProps(__spreadValues({}, item), {
                    label: item == null ? void 0 : item[labelKey],
                    value: item == null ? void 0 : item[valueKey],
                  }));
                  return Promise.resolve(data);
                }
                return Promise.resolve(res);
              }
              return Promise.resolve(res);
            }
            switch (response.status) {
              case 400:
                break;
              case 401:
                break;
              case 403:
              case 500:
                break;
            }
          } catch (err) {
            console.error('Request Failed', err);
            Promise.reject(err);
          }
        }));
        /***/ }),

      /***/ 1851:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';
        __webpack_require__.r(__webpack_exports__);
        /* harmony export */ __webpack_require__.d(__webpack_exports__, {
          /* harmony export */   capitalizeFirstLetter() {
            return /* binding */ capitalizeFirstLetter;
          },
          /* harmony export */   deepEquals() {
            return /* binding */ deepEquals;
          },
          /* harmony export */   gcd() {
            return /* binding */ gcd;
          },
          /* harmony export */   getBrowserlanguage() {
            return /* binding */ getBrowserlanguage;
          },
          /* harmony export */   getCookie() {
            return /* binding */ getCookie;
          },
          /* harmony export */   globalThisPolyfill() {
            return /* binding */ globalThisPolyfill;
          },
          /* harmony export */   hasOwnProperty() {
            return /* binding */ hasOwnProperty;
          },
          /* harmony export */   initializationValue() {
            return /* binding */ initializationValue;
          },
          /* harmony export */   intersection() {
            return /* binding */ intersection;
          },
          /* harmony export */   isObj() {
            return /* binding */ isObj;
          },
          /* harmony export */   isRegExp() {
            return /* binding */ isRegExp;
          },
          /* harmony export */   merge() {
            return /* binding */ merge;
          },
          /* harmony export */   mergeDeep() {
            return /* binding */ mergeDeep;
          },
          /* harmony export */   orderProperties() {
            return /* binding */ orderProperties;
          },
          /* harmony export */   scm() {
            return /* binding */ scm;
          },
          /* harmony export */   upperFirstLetter() {
            return /* binding */ upperFirstLetter;
          },
          /* harmony export */   valueType() {
            return /* binding */ valueType;
          },
          /* harmony export */ });

        const isRegExp = (regExpStr) => {
          let _a;
          return ((_a = new Function(`return ${regExpStr};`)()) == null ? void 0 : _a.constructor) === RegExp;
        };
        const isObj = val => Object.prototype.toString.call(val) === '[object Object]';
        const globalThisPolyfill = (function globalSelf() {
          try {
            if (typeof self !== 'undefined') {
              return self;
            }
          } catch (e) {
          }
          try {
            if (typeof window !== 'undefined') {
              return window;
            }
          } catch (e) {
          }
          try {
            if (typeof __webpack_require__.g !== 'undefined') {
              return __webpack_require__.g;
            }
          } catch (e) {
          }
          return Function('return this')();
        }());
        const getBrowserlanguage = () => {
          if (!globalThisPolyfill.navigator) {
            return 'zh';
          }
          return globalThisPolyfill.navigator.browserlanguage || globalThisPolyfill.navigator.language || 'zh';
        };
        const hasOwnProperty = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);
        const valueType = (value) => {
          if (Array.isArray(value)) {
            return 'array';
          }
          if (typeof value === 'string') {
            return 'string';
          }
          if (typeof value === 'boolean') {
            return 'boolean';
          }
          if (!isNaN(value)) {
            return 'number';
          }
          if (value === null) {
            return 'null';
          }
          if (typeof value === 'object') {
            return 'object';
          }
          return typeof value;
        };
        const merge = (target, source) => {
          if (isObj(source)) {
            return Object.keys(source).reduce((pre, key) => {
              pre[key] = merge((target == null ? void 0 : target[key]) || {}, source[key]);
              return pre;
            }, JSON.parse(JSON.stringify(target)));
          }
          if (Array.isArray(source)) {
            target = Array.isArray(target) ? target : [];
            return source.map((item, index) => {
              if (target[index]) {
                return merge(target[index], item);
              }
              return item;
            });
          }
          return source;
        };
        function intersection(arr1, arr2) {
          return arr1.filter(item => arr2.includes(item));
        }
        function gcd(a, b) {
          if (b === 0) return a;
          return gcd(b, a % b);
        }
        function scm(a, b) {
          return a * b / gcd(a, b);
        }
        function initializationValue(type, defaultInitValue = {
          integer: void 0,
          number: void 0,
          // 默认初始化值（number类型0值会有特殊含义）
        }) {
          switch (type) {
            case 'any':
              return void 0;
            case 'array':
              return [];
            case 'boolean':
              return false;
            case 'integer':
              return defaultInitValue.integer;
            case 'null':
              return null;
            case 'number':
              return defaultInitValue.number;
            case 'object':
              return {};
            case 'string':
              return '';
          }
        }
        function mergeDeep(target, ...sources) {
          if (!sources.length) return target;
          const source = sources.shift();
          if (isObj(target) && isObj(source)) {
            for (const key in source) {
              if (isObj(source[key])) {
                if (!target[key]) Object.assign(target, {
                  [key]: {},
                });
                mergeDeep(target[key], source[key]);
              } else {
                Object.assign(target, {
                  [key]: source[key],
                });
              }
            }
          }
          return mergeDeep(target, ...sources);
        }
        function isArguments(object) {
          return Object.prototype.toString.call(object) === '[object Arguments]';
        }
        function deepEquals(a, b, ca = [], cb = []) {
          if (a === b) {
            return true;
          }
          if (typeof a === 'function' || typeof b === 'function') {
            return true;
          }
          if (typeof a !== 'object' || typeof b !== 'object') {
            return false;
          }
          if (a === null || b === null) {
            return false;
          }
          if (a instanceof Date && b instanceof Date) {
            return a.getTime() === b.getTime();
          }
          if (a instanceof RegExp && b instanceof RegExp) {
            return a.source === b.source && a.global === b.global && a.multiline === b.multiline && a.lastIndex === b.lastIndex && a.ignoreCase === b.ignoreCase;
          }
          if (isArguments(a) || isArguments(b)) {
            if (!(isArguments(a) && isArguments(b))) {
              return false;
            }
            const { slice } = Array.prototype;
            return deepEquals(slice.call(a), slice.call(b), ca, cb);
          }
          if (a.constructor !== b.constructor) {
            return false;
          }
          const ka = Object.keys(a);
          const kb = Object.keys(b);
          if (ka.length === 0 && kb.length === 0) {
            return true;
          }
          if (ka.length !== kb.length) {
            return false;
          }
          let cal = ca.length;
          while (cal--) {
            if (ca[cal] === a) {
              return cb[cal] === b;
            }
          }
          ca.push(a);
          cb.push(b);
          ka.sort();
          kb.sort();
          for (let j = ka.length - 1; j >= 0; j--) {
            if (ka[j] !== kb[j]) {
              return false;
            }
          }
          let key;
          for (let k = ka.length - 1; k >= 0; k--) {
            key = ka[k];
            if (!deepEquals(a[key], b[key], ca, cb)) {
              return false;
            }
          }
          ca.pop();
          cb.pop();
          return true;
        }
        function orderProperties(properties, order) {
          if (!Array.isArray(order) || !order.length) {
            return properties;
          }
          const arrayToHash = arr => arr.reduce((prev, curr) => {
            prev[curr] = true;
            return prev;
          }, {});
          const errorPropList = arr => (arr.length > 1 ? `properties '${arr.join('\', \'')}'` : `property '${arr[0]}'`);
          const propertyHash = arrayToHash(properties);
          const orderFiltered = order.filter(prop => prop === '*' || propertyHash[prop]);
          const orderHash = arrayToHash(orderFiltered);
          const rest = properties.filter(prop => !orderHash[prop]);
          const restIndex = orderFiltered.indexOf('*');
          if (restIndex === -1) {
            if (rest.length) {
              throw new Error(`uiSchema order list does not contain ${errorPropList(rest)}`);
            }
            return orderFiltered;
          }
          if (restIndex !== orderFiltered.lastIndexOf('*')) {
            throw new Error('uiSchema order list contains more than one wildcard item');
          }
          const complete = [...orderFiltered];
          complete.splice(restIndex, 1, ...rest);
          return complete;
        }
        function upperFirstLetter(str) {
          if (!str) return str;
          return `${str.slice(0, 1).toUpperCase()}${str.slice(1)}`;
        }
        const getCookie = (name) => {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i];
            const [key, value] = cookie.split('=');
            if (key.trim() === name) {
              return value;
            }
          }
          return null;
        };
        function capitalizeFirstLetter(string) {
          return string.charAt(0).toUpperCase() + string.slice(1);
        }
        /***/ }),

      /***/ 2402:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';


        __webpack_require__(9749);
        __webpack_require__(8077);
        __webpack_require__(1919);
        __webpack_require__(7522);
        __webpack_require__(9474);
        const _interopRequireDefault = __webpack_require__(4836);
        Object.defineProperty(exports, '__esModule', ({
          value: true,
        }));
        exports.default = void 0;
        __webpack_require__(6801);
        __webpack_require__(9707);
        __webpack_require__(228);
        __webpack_require__(886);
        __webpack_require__(9358);
        const _vue = __webpack_require__(748);
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        const _widgetTree = _interopRequireDefault(__webpack_require__(7564));
        const _FieldProps = _interopRequireDefault(__webpack_require__(6620));
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        const _default = exports.default = (0, _vue.defineComponent)({
          name: 'FieldGroupWrap',
          props: _objectSpread(_objectSpread({}, _FieldProps.default), {}, {
            // 组类型
            type: {
              type: String,
              default: 'default',
              validator: function validator(value) {
                return ['default', 'normal', 'card'].includes(value);
              },
            },
            // 是否显示组title
            showTitle: {
              type: Boolean,
              default: false,
            },
            // 是否显示border
            border: {
              type: Boolean,
              default: false,
            },
            verifiable: {
              type: Boolean,
              default: false,
            },
            hideEmptyRow: {
              type: Boolean,
              default: false,
            },
          }),
          data: function data() {
            return {
              groupErrorTips: {},
              state: {
                // 组类型目前只支持visible
                visible: true,
              },
            };
          },
          created: function created() {
            // 注册widget TreeNode
            _widgetTree.default.addWidgetNode(this.path, this, 'group');
          },
          mounted: function mounted() {
            // 更新样式
            this.$forceUpdate();
          },
          beforeUnmount: function beforeUnmount() {
            _widgetTree.default.removeWidgetNode(this.path, this);
          },
          methods: {
            setState: function setState(key, value) {
              if (Reflect.has(this.state, key)) {
                this.state[key] = value;
              } else {
                console.warn('Group unsupported '.concat(key, ' state, please check'));
              }
            },
            setGroupErrorTips: function setGroupErrorTips(widgetPath, errorTips) {
              this.groupErrorTips[widgetPath] = errorTips;
            },
            removeGroupErrorTips: function removeGroupErrorTips(widgetPath) {
              delete this.groupErrorTips[widgetPath];
            },
            clearGroupErrorTips: function clearGroupErrorTips() {
              this.groupErrorTips = {};
            },
          },
          render: function render() {
            let _this$layout;
            let _this$layout2;
            let _this$schema;
            let _this$layout3;
            const _this = this;
            let _this$$slots;
            let _this$$slots$default;
            const schemaFormStyle = _objectSpread({
              position: 'relative',
              border: this.border ? '1px solid #dcdee5' : 'none',
              display: !this.state.visible ? 'none' : '',
            }, ((_this$layout = this.layout) === null || _this$layout === void 0 ? void 0 : _this$layout.item) || {});
            const groupContentStyle = _objectSpread({}, ((_this$layout2 = this.layout) === null || _this$layout2 === void 0 ? void 0 : _this$layout2.container) || {
              display: 'grid',
              gridGap: '20px', // 未设置layout的布局组的默认样式
            });
            const self = this;
            const renderDelete = function renderDelete() {
              return (0, _vue.h)('span', {
                class: ['bk-schema-form-group-delete'],
                style: {
                  right: '10px',
                  top: '10px',
                },
                onClick: function onClick() {
                  self.$emit('remove', self.path);
                },
              }, [(0, _vue.h)('i', {
                class: ['bk-icon icon-close3-shape'],
              })]);
            };
            const title = ((_this$schema = this.schema) === null || _this$schema === void 0 ? void 0 : _this$schema.title) || ((_this$layout3 = this.layout) === null || _this$layout3 === void 0 ? void 0 : _this$layout3.prop);
            const groupErrorTipsContent = Object.keys(this.groupErrorTips).map(widgetPath => (0, _vue.createVNode)('p', null, [_this.groupErrorTips[widgetPath]]));
            const hasError = JSON.stringify(this.groupErrorTips) !== '{}';
            return (0, _vue.createVNode)('div', {
              class: ['bk-schema-form-group', this.type, {
                'hide-empty-row': this.hideEmptyRow,
              }, {
                'bk-schema-form-group--error': hasError,
              }],
              style: schemaFormStyle,
            }, [title && this.showTitle ? (0, _vue.createVNode)('span', {
              class: ['bk-schema-form-group-title', this.type],
            }, [title, hasError ? (0, _vue.createVNode)('span', {
              class: 'bk-schema-form-group__error-tips',
            }, [(0, _vue.createVNode)('span', {
              class: 'bk-schema-form-group__error-tips-popover',
            }, [groupErrorTipsContent])]) : null]) : null, (0, _vue.createVNode)('div', {
              style: groupContentStyle,
              class: 'bk-schema-form-group-content',
            }, [(_this$$slots = this.$slots) === null || _this$$slots === void 0 || (_this$$slots$default = _this$$slots.default) === null || _this$$slots$default === void 0 ? void 0 : _this$$slots$default.call(_this$$slots)]), this.removeable && renderDelete()]);
          },
        });
        /***/ }),

      /***/ 8346:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';


        __webpack_require__(9358);
        __webpack_require__(9749);
        __webpack_require__(8077);
        __webpack_require__(228);
        __webpack_require__(1919);
        __webpack_require__(7522);
        __webpack_require__(9474);
        const _interopRequireDefault = __webpack_require__(4836);
        Object.defineProperty(exports, '__esModule', ({
          value: true,
        }));
        exports.default = void 0;
        __webpack_require__(4284);
        __webpack_require__(886);
        const _toConsumableArray2 = _interopRequireDefault(__webpack_require__(861));
        const _objectWithoutProperties2 = _interopRequireDefault(__webpack_require__(215));
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        const _schema = _interopRequireDefault(__webpack_require__(8683));
        const _vue = __webpack_require__(748);
        const _FieldProps = _interopRequireDefault(__webpack_require__(6620));
        const _Widget = _interopRequireDefault(__webpack_require__(5421));
        const _SchemaField = _interopRequireDefault(__webpack_require__(799));
        const _path = _interopRequireDefault(__webpack_require__(4879));
        const _util = __webpack_require__(1851);
        const _ArrayWidget = _interopRequireDefault(__webpack_require__(1975));
        const _excluded = ['name'];
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        const _default = exports.default = (0, _vue.defineComponent)({
          name: 'ArrayField',
          functional: true,
          props: _FieldProps.default,
          render: function render() {
            const _this = this;
            const _this$$props = this.$props;
            const { schema } = _this$$props;
            const { path } = _this$$props;
            if (_schema.default.isMultiSelect(schema) || _schema.default.isCustomArrayWidget(schema)) {
              // 多选类型 或 自定义数组类型（伪数组类型(只有一个FormItem，但是值为数组，值一般由自定义Widget控件决定)）
              return (0, _vue.h)(_Widget.default, _objectSpread(_objectSpread(_objectSpread({}, this.$props), this.$attrs), {}, {
                key: path,
                schema: (0, _util.mergeDeep)({
                  'ui:component': {
                    props: {
                      multiple: true,
                    },
                  },
                }, this.$props.schema),
              }), this.$slots);
            }
            // 元组类型
            if (_schema.default.isTupleArray(schema)) {
              const _Schema$getGroupWrap = _schema.default.getGroupWrap(schema);
              const { name } = _Schema$getGroupWrap;
              const vnode = (0, _objectWithoutProperties2.default)(_Schema$getGroupWrap, _excluded);
              const tupleVnodeList = schema.items.map((item, index) => (0, _vue.h)(_SchemaField.default, _objectSpread(_objectSpread(_objectSpread({}, _this.$props), _this.$attrs), {}, {
                key: _path.default.getCurPath(path, index),
                schema: item,
                path: _path.default.getCurPath(path, index),
              }), _this.$slots));
              return (0, _vue.h)(name, (0, _util.mergeDeep)(_objectSpread(_objectSpread({}, this.$props), {}, {
                path,
                showTitle: true,
              }), vnode), (0, _toConsumableArray2.default)(tupleVnodeList));
            }
            // 一般数组类型
            return (0, _vue.h)(_ArrayWidget.default, _objectSpread(_objectSpread({}, this.$attrs), this.$props), this.$slots);
          },
        });
        /***/ }),

      /***/ 1660:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';


        __webpack_require__(9358);
        __webpack_require__(9749);
        __webpack_require__(8077);
        __webpack_require__(228);
        __webpack_require__(1919);
        __webpack_require__(7522);
        __webpack_require__(9474);
        const _interopRequireDefault = __webpack_require__(4836);
        Object.defineProperty(exports, '__esModule', ({
          value: true,
        }));
        exports.default = void 0;
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        __webpack_require__(4284);
        __webpack_require__(6801);
        const _vue = __webpack_require__(748);
        const _FieldProps = _interopRequireDefault(__webpack_require__(6620));
        const _Widget = _interopRequireDefault(__webpack_require__(5421));
        const _util = __webpack_require__(1851);
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        const _default = exports.default = (0, _vue.defineComponent)({
          name: 'BooleanField',
          functional: true,
          props: _FieldProps.default,
          render: function render() {
            const _ref = this.$props.schema['ui:component'] || {};
            const { name } = _ref;
            let widgetProps = {};
            if (['radio', 'select'].includes(name)) {
              // radioGroup、select类型需要默认数据源
              widgetProps = {
                datasource: [{
                  label: 'False',
                  value: false,
                }, {
                  label: 'True',
                  value: true,
                }],
              };
            } else if (name === 'checkbox') {
              let _this$$props$schema;
              // boolean 类型checkbox
              widgetProps = {
                label: (_this$$props$schema = this.$props.schema) === null || _this$$props$schema === void 0 ? void 0 : _this$$props$schema.title,
              };
            }
            return (0, _vue.h)(_Widget.default, _objectSpread(_objectSpread(_objectSpread({}, this.$props), this.$attrs), {}, {
              schema: (0, _util.mergeDeep)({
                'ui:component': {
                  props: widgetProps,
                },
              }, this.$props.schema),
            }), this.$slots);
          },
        });
        /***/ }),

      /***/ 316:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';


        __webpack_require__(9749);
        __webpack_require__(1919);
        __webpack_require__(9474);
        const _interopRequireDefault = __webpack_require__(4836);
        Object.defineProperty(exports, '__esModule', ({
          value: true,
        }));
        exports.default = void 0;
        const _toConsumableArray2 = _interopRequireDefault(__webpack_require__(861));
        const _objectDestructuringEmpty2 = _interopRequireDefault(__webpack_require__(3012));
        const _typeof2 = _interopRequireDefault(__webpack_require__(8698));
        const _objectWithoutProperties2 = _interopRequireDefault(__webpack_require__(215));
        __webpack_require__(6801);
        __webpack_require__(9772);
        __webpack_require__(886);
        __webpack_require__(4284);
        __webpack_require__(228);
        __webpack_require__(429);
        __webpack_require__(9358);
        __webpack_require__(8077);
        __webpack_require__(7522);
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        const _path = _interopRequireDefault(__webpack_require__(4879));
        const _register = _interopRequireDefault(__webpack_require__(7859));
        const _schema = _interopRequireDefault(__webpack_require__(8683));
        const _util = __webpack_require__(1851);
        const _vue = __webpack_require__(748);
        const _FieldProps = _interopRequireDefault(__webpack_require__(6620));
        const _SchemaField = _interopRequireDefault(__webpack_require__(799));
        const _Widget = _interopRequireDefault(__webpack_require__(5421));
        const _validator = __webpack_require__(1837);
        const _excluded = ['name'];
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        const _default = exports.default = (0, _vue.defineComponent)({
          name: 'CompositionField',
          props: _objectSpread(_objectSpread({}, _FieldProps.default), {}, {
            composition: {
              type: String,
              default: 'oneOf',
              validator: function validator(value) {
                return ['oneOf', 'anyOf'].includes(value);
              },
            },
          }),
          data: function data() {
            return {
              activeIndex: -1,
            };
          },
          created: function created() {
            const _this = this;
            // 初始化默认 composition 选项
            const compositionList = this.schema[this.composition] || [];
            // todo 没有required选项时回显不成功
            const index = compositionList.findIndex(item => _validator.ajv.validate(item, _this.modelValue));
            this.activeIndex = index > -1 ? index : 0;
          },
          render: function render() {
            const _this2 = this;
            const compositionList = this.schema[this.composition] || [];
            const schemaList = compositionList.map((item) => {
              const data = (0, _util.mergeDeep)({}, _this2.schema, item);
              delete data[_this2.composition];
              return data;
            });
            const _Schema$getUiProps = _schema.default.getUiProps('ui:'.concat(this.composition), this.schema);
            const _Schema$getUiProps$na = _Schema$getUiProps.name;
            const com = _Schema$getUiProps$na === void 0 ? 'radio' : _Schema$getUiProps$na;
            const vnodeData = (0, _objectWithoutProperties2.default)(_Schema$getUiProps, _excluded);
            const isConst = (0, _typeof2.default)(this.schema.type) !== 'object' && schemaList.every(item => item.const);
            if (isConst) {
              // 全是常量
              return (0, _vue.h)(_Widget.default, _objectSpread(_objectSpread({}, this.$props), this.$attrs), this.$slots);
            }
            const _Schema$getUiProps2 = _schema.default.getUiProps('ui:composition', this.schema);
            const compositionVnodeData = Object.assign({}, ((0, _objectDestructuringEmpty2.default)(_Schema$getUiProps2), _Schema$getUiProps2));
            return (0, _vue.h)(_register.default.getComponent('group'), (0, _util.mergeDeep)(_objectSpread(_objectSpread({}, this.$props), {}, {
              rootData: this.rootData,
              schema: this.schema,
              modelValue: _path.default.getPathVal(this.rootData, this.path),
              path: this.path,
              onRemove: function onRemove() {
                this.$emit('remove', this.path);
              },
            }), compositionVnodeData), [
              // anyOf component
              (0, _vue.h)(_register.default.getBaseWidget('form-item'), {
                label: vnodeData === null || vnodeData === void 0 ? void 0 : vnodeData.title,
              }, [(0, _vue.h)(_register.default.getComponent(com), (0, _util.mergeDeep)({
                modelValue: this.activeIndex,
                datasource: schemaList.map((item, index) => ({
                  label: item.title || '',
                  value: index,
                })),
                clearable: false,
                'onUpdate:modelValue': function onUpdateModelValue(index) {
                  _this2.activeIndex = index;
                  // todo 删除其他 composition 字段
                  if ((0, _util.isObj)(_this2.modelValue)) {
                    const newValue = JSON.parse(JSON.stringify(_this2.modelValue));
                    const _props = compositionList.filter((_, index) => index !== _this2.activeIndex).reduce((pre, item) => {
                      const _item$properties = item.properties;
                      const properties = _item$properties === void 0 ? {} : _item$properties;
                      pre.push.apply(pre, (0, _toConsumableArray2.default)(Object.keys(properties)));
                      return pre;
                    }, []);
                    _props.forEach((prop) => {
                      delete newValue[prop];
                    });
                    _this2.$emit('update:modelValue', {
                      path: _this2.path,
                      value: newValue,
                    });
                  }
                },
              }, vnodeData || {}))]),
              // schema
              (0, _vue.h)(_SchemaField.default, _objectSpread(_objectSpread(_objectSpread({}, this.$props), this.$attrs), {}, {
                key: this.activeIndex,
                removeable: false,
                schema: schemaList[this.activeIndex],
              }), this.$slots)]);
          },
        });
        /***/ }),

      /***/ 7691:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';


        __webpack_require__(9358);
        __webpack_require__(9749);
        __webpack_require__(8077);
        __webpack_require__(228);
        __webpack_require__(1919);
        __webpack_require__(7522);
        __webpack_require__(9474);
        const _interopRequireDefault = __webpack_require__(4836);
        Object.defineProperty(exports, '__esModule', ({
          value: true,
        }));
        exports.default = void 0;
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        const _util = __webpack_require__(1851);
        const _vue = __webpack_require__(748);
        const _FieldProps = _interopRequireDefault(__webpack_require__(6620));
        const _StringField = _interopRequireDefault(__webpack_require__(2576));
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        const _default = exports.default = (0, _vue.defineComponent)({
          name: 'NumberField',
          functional: true,
          props: _FieldProps.default,
          render: function render() {
            let _this$$props$schema;
            return (0, _vue.h)(_StringField.default, _objectSpread(_objectSpread(_objectSpread({}, this.$props), this.$attrs), {}, {
              schema: (0, _util.mergeDeep)({
                'ui:component': {
                  props: {
                    type: 'number',
                    min: ((_this$$props$schema = this.$props.schema) === null || _this$$props$schema === void 0 ? void 0 : _this$$props$schema.type) === 'integer' ? 0 : -Infinity,
                  },
                },
              }, this.$props.schema),
            }), this.$slots);
          },
        });
        /***/ }),

      /***/ 9921:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';


        __webpack_require__(9749);
        __webpack_require__(8077);
        __webpack_require__(228);
        __webpack_require__(1919);
        __webpack_require__(7522);
        __webpack_require__(9474);
        const _interopRequireDefault = __webpack_require__(4836);
        Object.defineProperty(exports, '__esModule', ({
          value: true,
        }));
        exports.default = void 0;
        const _toConsumableArray2 = _interopRequireDefault(__webpack_require__(861));
        const _objectWithoutProperties2 = _interopRequireDefault(__webpack_require__(215));
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        __webpack_require__(9358);
        __webpack_require__(886);
        __webpack_require__(4284);
        const _vue = __webpack_require__(748);
        const _FieldProps = _interopRequireDefault(__webpack_require__(6620));
        const _SchemaField = _interopRequireDefault(__webpack_require__(799));
        const _schema = _interopRequireDefault(__webpack_require__(8683));
        const _path = _interopRequireDefault(__webpack_require__(4879));
        const _layout = _interopRequireDefault(__webpack_require__(3570));
        const _util = __webpack_require__(1851);
        const _Widget = _interopRequireDefault(__webpack_require__(5421));
        const _excluded = ['name'];
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        const _default2 = exports.default = (0, _vue.defineComponent)({
          name: 'ObjectField',
          functional: true,
          props: _FieldProps.default,
          render: function render() {
            const _this = this;
            const _this$$props = this.$props;
            const { schema } = _this$$props;
            const { path } = _this$$props;
            const { layout } = _this$$props;
            const { rootData } = _this$$props;
            const properties = (0, _util.orderProperties)(Object.keys(schema.properties || {}), schema['ui:order']);
            let vNodeList = [];
            if (properties.length) {
              vNodeList = properties.map((name) => {
                let _schema$properties;
                const curPath = _path.default.getCurPath(path, name);
                const lastProp = curPath.split('.').pop();
                const layoutConfig = _layout.default.findLayoutByProp(lastProp, layout.group || []) || {};
                return (0, _vue.h)(_SchemaField.default, _objectSpread(_objectSpread(_objectSpread({}, _this.$props), _this.$attrs), {}, {
                  key: curPath,
                  modelValue: _path.default.getPathVal(rootData, curPath),
                  schema: (_schema$properties = schema.properties) === null || _schema$properties === void 0 ? void 0 : _schema$properties[name],
                  required: _schema.default.isRequired(schema, name),
                  path: curPath,
                  layout: layoutConfig,
                  removeable: false, // todo: 不往下传递可删除属性
                }));
              });
            } else if (_schema.default.getUiComponent(schema)) {
              // 如果object属性没有配置 Properties，但是有ui:component属性，那个直接渲染对应的组件
              vNodeList = [(0, _vue.h)(_Widget.default, _objectSpread(_objectSpread({}, this.$props), this.$attrs), this.$slots)];
            }
            const _Schema$getGroupWrap = _schema.default.getGroupWrap(schema);
            const { name } = _Schema$getGroupWrap;
            const vnodeData = (0, _objectWithoutProperties2.default)(_Schema$getGroupWrap, _excluded);
            return (0, _vue.h)(name, (0, _util.mergeDeep)(_objectSpread(_objectSpread(_objectSpread({}, this.$props), this.$attrs), {}, {
              modelValue: _path.default.getPathVal(rootData, path),
              path,
            }), vnodeData), {
              default: function _default() {
                return (0, _toConsumableArray2.default)(vNodeList);
              },
            });
          },
        });
        /***/ }),

      /***/ 799:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';


        __webpack_require__(9749);
        __webpack_require__(8077);
        __webpack_require__(228);
        __webpack_require__(1919);
        __webpack_require__(7522);
        __webpack_require__(9474);
        const _interopRequireDefault = __webpack_require__(4836);
        Object.defineProperty(exports, '__esModule', ({
          value: true,
        }));
        exports.default = void 0;
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        __webpack_require__(9358);
        __webpack_require__(4284);
        const _vue = __webpack_require__(748);
        const _schema = _interopRequireDefault(__webpack_require__(8683));
        const _FieldProps = _interopRequireDefault(__webpack_require__(6620));
        const _path = _interopRequireDefault(__webpack_require__(4879));
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        const _default = exports.default = (0, _vue.defineComponent)({
          name: 'SchemaField',
          functional: true,
          props: _FieldProps.default,
          render: function render() {
            const _this$$props = this.$props;
            const { schema } = _this$$props;
            const { rootData } = _this$$props;
            const { path } = _this$$props;
            const resolveSchema = _schema.default.resolveSchema(schema);
            if (!Object.keys(schema).length) return null;
            const _Schema$getSchemaFiel = _schema.default.getSchemaField(resolveSchema);
            const { name } = _Schema$getSchemaFiel;
            const fieldProps = _Schema$getSchemaFiel.props;
            return name ? (0, _vue.h)(name, _objectSpread(_objectSpread(_objectSpread(_objectSpread({}, this.$attrs), this.$props), fieldProps), {}, {
              modelValue: _path.default.getPathVal(rootData, path),
              schema: resolveSchema,
            }), this.$slots) : null;
          },
        });
        /***/ }),

      /***/ 2576:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';


        __webpack_require__(9358);
        __webpack_require__(9749);
        __webpack_require__(8077);
        __webpack_require__(228);
        __webpack_require__(1919);
        __webpack_require__(7522);
        __webpack_require__(9474);
        const _interopRequireDefault = __webpack_require__(4836);
        Object.defineProperty(exports, '__esModule', ({
          value: true,
        }));
        exports.default = void 0;
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        const _vue = __webpack_require__(748);
        const _Widget = _interopRequireDefault(__webpack_require__(5421));
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        const StringField = function StringField(props, ctx) {
          return (0, _vue.h)(_Widget.default, _objectSpread(_objectSpread({}, props), ctx.attrs), ctx.slots);
        };
        const _default = exports.default = StringField;
        /***/ }),

      /***/ 5944:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';


        __webpack_require__(9749);
        __webpack_require__(8077);
        __webpack_require__(228);
        __webpack_require__(1919);
        __webpack_require__(7522);
        __webpack_require__(9474);
        const _interopRequireDefault = __webpack_require__(4836);
        Object.defineProperty(exports, '__esModule', ({
          value: true,
        }));
        exports.default = void 0;
        __webpack_require__(7895);
        __webpack_require__(4338);
        __webpack_require__(9358);
        __webpack_require__(2506);
        __webpack_require__(6203);
        __webpack_require__(886);
        const _vue = __webpack_require__(748);
        const _toConsumableArray2 = _interopRequireDefault(__webpack_require__(861));
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        const _schema = _interopRequireDefault(__webpack_require__(8683));
        const _SchemaField = _interopRequireDefault(__webpack_require__(799));
        const _FieldProps = _interopRequireDefault(__webpack_require__(6620));
        const _path = _interopRequireDefault(__webpack_require__(4879));
        const _layout = _interopRequireDefault(__webpack_require__(3570));
        const _util = __webpack_require__(1851);
        const _FieldGroupWrap = _interopRequireDefault(__webpack_require__(2402));
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        // 伪数组类型
        const _default2 = exports.default = (0, _vue.defineComponent)({
          name: 'KeyValueArrayWidget',
          props: _objectSpread(_objectSpread({}, _FieldProps.default), {}, {
            // 当前值
            modelValue: {
              type: Array,
              default: function _default() {
                return [];
              },
            },
          }),
          mounted: function mounted() {
            let _this$modelValue;
            const _this$schema$minItems = this.schema.minItems;
            const minItems = _this$schema$minItems === void 0 ? 0 : _this$schema$minItems;
            // 补全minItems项
            if (((_this$modelValue = this.modelValue) === null || _this$modelValue === void 0 ? void 0 : _this$modelValue.length) < minItems) {
              const data = _schema.default.getSchemaDefaultValue(this.schema.items);
              const remainData = new Array(minItems - this.modelValue.length).fill(data);
              this.$emit('update:modelValue', [].concat((0, _toConsumableArray2.default)(this.modelValue), (0, _toConsumableArray2.default)(remainData)));
            }
          },
          methods: {
            handleAddItem: function handleAddItem() {
              if (this.disabled) return;
              const data = _schema.default.getSchemaDefaultValue(this.schema.items);
              this.$emit('update:modelValue', [].concat((0, _toConsumableArray2.default)(this.modelValue), [data]));
            },
            handleRemoveItem: function handleRemoveItem(index) {
              if (this.disabled) return;
              const value = JSON.parse(JSON.stringify(this.modelValue));
              value.splice(index, 1);
              this.$emit('update:modelValue', value);
            },
            handleInput: function handleInput(_ref) {
              const { path } = _ref;
              const { value } = _ref;
              // 捕获widget input事件，包装继续传给上一层处理
              const subPath = _path.default.getSubPath(this.path, path);
              const newValue = _path.default.setPathValue(this.modelValue, subPath, value);
              this.$emit('update:modelValue', newValue);
            },
          },
          render: function render() {
            let _this$schema;
            let _this$schema2;
            const _this = this;
            let _this$modelValue2;
            const labelBtnStyle = {
              'font-size': '16px',
              color: '#979ba5',
              cursor: this.disabled ? 'not-allowed' : 'pointer',
              display: 'inline-block',
            };
            const properties = (_this$schema = this.schema) === null || _this$schema === void 0 || (_this$schema = _this$schema.items) === null || _this$schema === void 0 ? void 0 : _this$schema.properties;
            const props = (0, _util.orderProperties)(Object.keys(properties || {}), (_this$schema2 = this.schema) === null || _this$schema2 === void 0 || (_this$schema2 = _this$schema2.items) === null || _this$schema2 === void 0 ? void 0 : _this$schema2['ui:order']);
            // props为空时，表示只有一个项
            const keysLen = Object.keys(properties || {}).length;
            const defaultCols = properties ? new Array(keysLen).fill('1fr')
              .concat('20px')
              .join(' ') : '1fr 20px';
            const defaultContainerLayout = _objectSpread({}, this.layout.container || {
              display: 'grid',
              gridGap: '20px',
              'grid-template-columns': defaultCols, // 默认配置
            });
            const self = this;
            const dealSchema = function dealSchema(schema) {
              return (
              // 处理当前控件默认Schema配置逻辑
                (0, _util.mergeDeep)({
                  'ui:component': {
                    props: {
                      placeholder: schema.title,
                    },
                  },
                  'ui:props': {
                    // 默认不展示标题
                    showTitle: false,
                    // 0.1 兼容formItem设置 labelWidth 0 不生效问题
                    labelWidth: 0.1,
                  },
                }, schema)
              );
            };
            const renderSchemaField = function renderSchemaField(data) {
              const { path } = data;
              const { schema } = data;
              const { required } = data;
              const { layout } = data;
              return (0, _vue.h)(_SchemaField.default, _objectSpread(_objectSpread({}, _this.$props), {}, {
                key: path,
                schema,
                required,
                path,
                layout,
                style: {
                  marginBottom: '10px',
                },
                'onUpdate:modelValue': function onUpdateModelValue(data) {
                  self.handleInput(data);
                },
              }));
            };
            return (0, _vue.createVNode)('div', null, [(_this$modelValue2 = this.modelValue) === null || _this$modelValue2 === void 0 ? void 0 : _this$modelValue2.map((_, index) => {
              let _this$schema4;
              const groupPath = _path.default.getCurPath(_this.path, ''.concat(index));
              return (0, _vue.createVNode)(_FieldGroupWrap.default, _objectSpread(_objectSpread({}, _this.$props), {}, {
                path: groupPath,
                modelValue: _path.default.getPathVal(_this.rootData, groupPath),
                schema: _this.schema.items,
                layout: _objectSpread(_objectSpread({}, _this.layout), {}, {
                  container: _objectSpread({}, defaultContainerLayout),
                }),
              }), {
                default: function _default() {
                  return [props !== null && props !== void 0 && props.length ? props.map((prop) => {
                    let _this$schema3;
                    const schemaItem = (_this$schema3 = _this.schema) === null || _this$schema3 === void 0 || (_this$schema3 = _this$schema3.items) === null || _this$schema3 === void 0 ? void 0 : _this$schema3.properties[prop];
                    const curPath = _path.default.getCurPath(_this.path, ''.concat(index, '.').concat(prop));
                    const lastProp = curPath.split('.').pop();
                    const layoutConfig = _layout.default.findLayoutByProp(lastProp, _this.layout.group || []) || {};
                    return renderSchemaField({
                      path: curPath,
                      schema: dealSchema(schemaItem),
                      layout: layoutConfig,
                      required: _schema.default.isRequired(schemaItem, prop),
                    });
                  }) : renderSchemaField({
                    path: _path.default.getCurPath(_this.path, index),
                    schema: dealSchema(((_this$schema4 = _this.schema) === null || _this$schema4 === void 0 ? void 0 : _this$schema4.items) || {}),
                    layout: {},
                    required: false,
                  }), (0, _vue.createVNode)('span', {
                    style: labelBtnStyle,
                    onClick: function onClick() {
                      return _this.handleRemoveItem(index);
                    },
                  }, [(0, _vue.createVNode)('i', {
                    class: 'bk-icon icon-minus-line',
                  }, null)])];
                },
              });
            }), (0, _vue.createVNode)('span', {
              onClick: this.handleAddItem,
              style: labelBtnStyle,
            }, [(0, _vue.createVNode)('i', {
              class: 'bk-icon icon-plus-line',
            }, null)])]);
          },
        });
        /***/ }),

      /***/ 5502:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';
        let __webpack_unused_export__;


        __webpack_require__(9358);
        __webpack_require__(9749);
        __webpack_require__(8077);
        __webpack_require__(228);
        __webpack_require__(1919);
        __webpack_require__(7522);
        __webpack_require__(9474);
        __webpack_require__(752);
        __webpack_require__(1694);
        __webpack_require__(1090);
        __webpack_require__(6265);
        const _interopRequireDefault = __webpack_require__(4836);
        const _typeof = __webpack_require__(8698);
        __webpack_unused_export__ = ({
          value: true,
        });
        exports.Z = createForm;
        const _defineProperty2 = _interopRequireDefault(__webpack_require__(8416));
        const _vue = __webpack_require__(748);
        const _util = __webpack_require__(1851);
        const _register = _interopRequireWildcard(__webpack_require__(7859));
        const _schema = _interopRequireDefault(__webpack_require__(8683));
        const _layout = _interopRequireDefault(__webpack_require__(3570));
        const _proxy = _interopRequireDefault(__webpack_require__(4865));
        const _path = _interopRequireDefault(__webpack_require__(4879));
        const _props = _interopRequireDefault(__webpack_require__(7213));
        const _SchemaField = _interopRequireDefault(__webpack_require__(799));
        const _ObjectField = _interopRequireDefault(__webpack_require__(9921));
        const _NumberField = _interopRequireDefault(__webpack_require__(7691));
        const _StringField = _interopRequireDefault(__webpack_require__(2576));
        const _ArrayField = _interopRequireDefault(__webpack_require__(8346));
        const _BooleanField = _interopRequireDefault(__webpack_require__(1660));
        const _CompositionField = _interopRequireDefault(__webpack_require__(316));
        const _CheckboxWidget = _interopRequireDefault(__webpack_require__(5341));
        const _SelectWidget = _interopRequireDefault(__webpack_require__(8985));
        const _RadioWidget = _interopRequireDefault(__webpack_require__(2544));
        const _ButtonWidget = _interopRequireDefault(__webpack_require__(8194));
        const _TableWidget = _interopRequireDefault(__webpack_require__(294));
        const _FieldGroupWrap = _interopRequireDefault(__webpack_require__(2402));
        const _KeyValueArrayWidget = _interopRequireDefault(__webpack_require__(5944));
        const _TabGroupWidget = _interopRequireDefault(__webpack_require__(5307));
        const _CollapseGroupWidget = _interopRequireDefault(__webpack_require__(1272));
        const _SwitchWidget = _interopRequireDefault(__webpack_require__(5638));
        const _ColorPickerWidget = _interopRequireDefault(__webpack_require__(9376));
        const _InputWidget = _interopRequireDefault(__webpack_require__(9442));
        __webpack_require__(2834);
        const _validator = __webpack_require__(1837);
        function _getRequireWildcardCache(e) {
          if ('function' !== typeof WeakMap) return null; const r = new WeakMap(); const t = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(e) {
            return e ? t : r;
          })(e);
        }
        function _interopRequireWildcard(e, r) {
          if (!r && e && e.__esModule) return e; if (null === e || 'object' != _typeof(e) && 'function' !== typeof e) return { default: e }; const t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); const n = { __proto__: null }; const a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (const u in e) if ('default' !== u && Object.prototype.hasOwnProperty.call(e, u)) {
            const i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u];
          } return n.default = e, t && t.set(e, n), n;
        }
        function ownKeys(e, r) {
          const t = Object.keys(e); if (Object.getOwnPropertySymbols) {
            let o = Object.getOwnPropertySymbols(e); r && (o = o.filter(r => Object.getOwnPropertyDescriptor(e, r).enumerable)), t.push.apply(t, o);
          } return t;
        }
        function _objectSpread(e) {
          for (let r = 1; r < arguments.length; r++) {
            var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach((r) => {
              (0, _defineProperty2.default)(e, r, t[r]);
            }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((r) => {
              Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
            });
          } return e;
        }
        const defaultOptions = {
          namespace: 'bk',
          components: {
            button: _ButtonWidget.default,
            select: _SelectWidget.default,
            radio: _RadioWidget.default,
            checkbox: _CheckboxWidget.default,
            table: _TableWidget.default,
            group: _FieldGroupWrap.default,
            bfArray: _KeyValueArrayWidget.default,
            tab: _TabGroupWidget.default,
            collapse: _CollapseGroupWidget.default,
            switcher: _SwitchWidget.default,
            color: _ColorPickerWidget.default,
            bfInput: _InputWidget.default,
          },
          fields: {
            object: _ObjectField.default,
            string: _StringField.default,
            any: '',
            array: _ArrayField.default,
            boolean: _BooleanField.default,
            null: '',
            integer: _NumberField.default,
            number: _NumberField.default,
            composition: _CompositionField.default,
          },
        };
        function createForm() {
          const opts = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
          const options = (0, _util.mergeDeep)(defaultOptions, opts);
          const { namespace } = options;
          const { components } = options;
          const { fields } = options;
          const _options$baseWidgets = options.baseWidgets;
          const baseWidgets = _options$baseWidgets === void 0 ? {} : _options$baseWidgets;
          _register.Registry.namespace = namespace;
          _register.default.addComponentsMap(components);
          _register.default.addFieldsMap(fields);
          _register.default.addBaseWidgets(baseWidgets);
          return (0, _vue.defineComponent)({
            name: 'BkuiForm',
            props: _props.default,
            data: function data() {
              return {
                rootData: {},
                formKey: 'bk-ui-form',
              };
            },
            watch: {
              schema: function schema(newSchema, oldSchema) {
                if (JSON.stringify(newSchema) === JSON.stringify(oldSchema)) return;
                this.validateSchema(this.schema);
                this.initFormData();
                this.formKey = 'bk-ui-form-'.concat(new Date().getTime());
              },
              context: {
                handler: function handler(ctx) {
                  _register.Registry.context = ctx;
                  if ((0, _util.hasOwnProperty)(ctx, 'rules')) {
                    (0, _validator.registryGlobalRules)(ctx.rules);
                  }
                },
                immediate: true,
              },
              rules: {
                immediate: true,
                handler: function handler(value) {
                  (0, _validator.registryGlobalRules)(value);
                },
              },
              modelValue: function modelValue() {
                this.initFormData();
              },
            },
            beforeCreate: function beforeCreate() {
              (0, _validator.registryGlobalRules)(_validator.DEFAULT_RULES);
            },
            created: function created() {
              this.validateSchema(this.schema);
              this.initFormData();
            },
            methods: {
              initFormData: function initFormData() {
                this.rootData = (0, _util.merge)(_schema.default.getSchemaDefaultValue((0, _proxy.default)(this.schema, this)) || {}, this.modelValue);
                this.emitFormValueChange(this.rootData, this.modelValue);
              },
              emitFormValueChange: function emitFormValueChange(newValue, oldValue) {
                if (!(0, _util.deepEquals)(newValue, oldValue)) {
                  this.rootData = newValue;
                  this.$emit('update:modelValue', newValue);
                  this.$emit('change', newValue, oldValue);
                }
              },
              validateForm: _validator.validateForm,
              validateFormItem: _validator.validateFormItem,
              validate: _validator.validateFormWithResult,
              validateSchema: _validator.validateSchema,
            },
            render: function render() {
              const _this = this;
              const self = this;
              return (0, _vue.h)(_register.default.getBaseWidget('form'), {
                ref: 'bkui-form',
                key: this.formKey,
                model: this.modelValue,
                formType: this.formType,
                labelWidth: this.labelWidth,
                class: {
                  'bk-schema-form': true,
                },
                style: {
                  width: typeof this.width === 'number' ? ''.concat(this.width, 'px') : this.width,
                },
              }, {
                default: function _default() {
                  return (0, _vue.h)(_SchemaField.default, _objectSpread(_objectSpread({}, _this.$props), {}, {
                    schema: (0, _proxy.default)(_this.schema, _this),
                    rootData: _this.rootData,
                    modelValue: _this.modelValue,
                    layout: new _layout.default(_this.layout).layout,
                    'onUpdate:modelValue': function onUpdateModelValue(_ref) {
                      const _ref$path = _ref.path;
                      const path = _ref$path === void 0 ? '' : _ref$path;
                      const { value } = _ref;
                      if (!path) {
                        // console.warn('set rootData');
                        self.emitFormValueChange(value, self.modelValue);
                      } else {
                        // 双向绑定逻辑
                        const newValue = _path.default.setPathValue(self.rootData, path, value);
                        self.emitFormValueChange(newValue, self.modelValue);
                      }
                    },
                  }), _this.$slots);
                },
              });
            },
          });
        }
        /***/ }),

      /***/ 540:
      /***/ (function (__unused_webpack_module, exports) {
        /** @license URI.js v4.4.1 (c) 2011 Gary Court. License: http://github.com/garycourt/uri-js */
        (function (global, factory) {
	 true ? factory(exports)
            : 0;
        }(this, ((exports) => {
          'use strict';

          function merge() {
            for (var _len = arguments.length, sets = Array(_len), _key = 0; _key < _len; _key++) {
              sets[_key] = arguments[_key];
            }

            if (sets.length > 1) {
              sets[0] = sets[0].slice(0, -1);
              const xl = sets.length - 1;
              for (let x = 1; x < xl; ++x) {
                sets[x] = sets[x].slice(1, -1);
              }
              sets[xl] = sets[xl].slice(1);
              return sets.join('');
            }
            return sets[0];
          }
          function subexp(str) {
            return `(?:${str})`;
          }
          function typeOf(o) {
            return o === undefined ? 'undefined' : o === null ? 'null' : Object.prototype.toString.call(o).split(' ')
              .pop()
              .split(']')
              .shift()
              .toLowerCase();
          }
          function toUpperCase(str) {
            return str.toUpperCase();
          }
          function toArray(obj) {
            return obj !== undefined && obj !== null ? obj instanceof Array ? obj : typeof obj.length !== 'number' || obj.split || obj.setInterval || obj.call ? [obj] : Array.prototype.slice.call(obj) : [];
          }
          function assign(target, source) {
            const obj = target;
            if (source) {
              for (const key in source) {
                obj[key] = source[key];
              }
            }
            return obj;
          }

          function buildExps(isIRI) {
            const ALPHA$$ = '[A-Za-z]';
            const CR$ = '[\\x0D]';
            const DIGIT$$ = '[0-9]';
            const DQUOTE$$ = '[\\x22]';
            const HEXDIG$$ = merge(DIGIT$$, '[A-Fa-f]');
            // case-insensitive
            const LF$$ = '[\\x0A]';
            const SP$$ = '[\\x20]';
            const PCT_ENCODED$ = subexp(`${subexp(`%[EFef]${HEXDIG$$}%${HEXDIG$$}${HEXDIG$$}%${HEXDIG$$}${HEXDIG$$}`)}|${subexp(`%[89A-Fa-f]${HEXDIG$$}%${HEXDIG$$}${HEXDIG$$}`)}|${subexp(`%${HEXDIG$$}${HEXDIG$$}`)}`);
            // expanded
            const GEN_DELIMS$$ = '[\\:\\/\\?\\#\\[\\]\\@]';
            const SUB_DELIMS$$ = '[\\!\\$\\&\\\'\\(\\)\\*\\+\\,\\;\\=]';
            const RESERVED$$ = merge(GEN_DELIMS$$, SUB_DELIMS$$);
            const UCSCHAR$$ = isIRI ? '[\\xA0-\\u200D\\u2010-\\u2029\\u202F-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF]' : '[]';
            // subset, excludes bidi control characters
            const IPRIVATE$$ = isIRI ? '[\\uE000-\\uF8FF]' : '[]';
            // subset
            const UNRESERVED$$ = merge(ALPHA$$, DIGIT$$, '[\\-\\.\\_\\~]', UCSCHAR$$);
            const SCHEME$ = subexp(`${ALPHA$$ + merge(ALPHA$$, DIGIT$$, '[\\+\\-\\.]')}*`);
            const USERINFO$ = subexp(`${subexp(`${PCT_ENCODED$}|${merge(UNRESERVED$$, SUB_DELIMS$$, '[\\:]')}`)}*`);
            const DEC_OCTET$ = subexp(`${subexp('25[0-5]')}|${subexp(`2[0-4]${DIGIT$$}`)}|${subexp(`1${DIGIT$$}${DIGIT$$}`)}|${subexp(`[1-9]${DIGIT$$}`)}|${DIGIT$$}`);
            const DEC_OCTET_RELAXED$ = subexp(`${subexp('25[0-5]')}|${subexp(`2[0-4]${DIGIT$$}`)}|${subexp(`1${DIGIT$$}${DIGIT$$}`)}|${subexp(`0?[1-9]${DIGIT$$}`)}|0?0?${DIGIT$$}`);
            // relaxed parsing rules
            const IPV4ADDRESS$ = subexp(`${DEC_OCTET_RELAXED$}\\.${DEC_OCTET_RELAXED$}\\.${DEC_OCTET_RELAXED$}\\.${DEC_OCTET_RELAXED$}`);
            const H16$ = subexp(`${HEXDIG$$}{1,4}`);
            const LS32$ = subexp(`${subexp(`${H16$}\\:${H16$}`)}|${IPV4ADDRESS$}`);
            const IPV6ADDRESS1$ = subexp(`${subexp(`${H16$}\\:`)}{6}${LS32$}`);
            //                           6( h16 ":" ) ls32
            const IPV6ADDRESS2$ = subexp(`\\:\\:${subexp(`${H16$}\\:`)}{5}${LS32$}`);
            //                      "::" 5( h16 ":" ) ls32
            const IPV6ADDRESS3$ = subexp(`${subexp(H16$)}?\\:\\:${subexp(`${H16$}\\:`)}{4}${LS32$}`);
            // [               h16 ] "::" 4( h16 ":" ) ls32
            const IPV6ADDRESS4$ = subexp(`${subexp(`${subexp(`${H16$}\\:`)}{0,1}${H16$}`)}?\\:\\:${subexp(`${H16$}\\:`)}{3}${LS32$}`);
            // [ *1( h16 ":" ) h16 ] "::" 3( h16 ":" ) ls32
            const IPV6ADDRESS5$ = subexp(`${subexp(`${subexp(`${H16$}\\:`)}{0,2}${H16$}`)}?\\:\\:${subexp(`${H16$}\\:`)}{2}${LS32$}`);
            // [ *2( h16 ":" ) h16 ] "::" 2( h16 ":" ) ls32
            const IPV6ADDRESS6$ = subexp(`${subexp(`${subexp(`${H16$}\\:`)}{0,3}${H16$}`)}?\\:\\:${H16$}\\:${LS32$}`);
            // [ *3( h16 ":" ) h16 ] "::"    h16 ":"   ls32
            const IPV6ADDRESS7$ = subexp(`${subexp(`${subexp(`${H16$}\\:`)}{0,4}${H16$}`)}?\\:\\:${LS32$}`);
            // [ *4( h16 ":" ) h16 ] "::"              ls32
            const IPV6ADDRESS8$ = subexp(`${subexp(`${subexp(`${H16$}\\:`)}{0,5}${H16$}`)}?\\:\\:${H16$}`);
            // [ *5( h16 ":" ) h16 ] "::"              h16
            const IPV6ADDRESS9$ = subexp(`${subexp(`${subexp(`${H16$}\\:`)}{0,6}${H16$}`)}?\\:\\:`);
            // [ *6( h16 ":" ) h16 ] "::"
            const IPV6ADDRESS$ = subexp([IPV6ADDRESS1$, IPV6ADDRESS2$, IPV6ADDRESS3$, IPV6ADDRESS4$, IPV6ADDRESS5$, IPV6ADDRESS6$, IPV6ADDRESS7$, IPV6ADDRESS8$, IPV6ADDRESS9$].join('|'));
            const ZONEID$ = subexp(`${subexp(`${UNRESERVED$$}|${PCT_ENCODED$}`)}+`);
            // RFC 6874
            const IPV6ADDRZ$ = subexp(`${IPV6ADDRESS$}\\%25${ZONEID$}`);
            // RFC 6874
            const IPV6ADDRZ_RELAXED$ = subexp(IPV6ADDRESS$ + subexp(`\\%25|\\%(?!${HEXDIG$$}{2})`) + ZONEID$);
            // RFC 6874, with relaxed parsing rules
            const IPVFUTURE$ = subexp(`[vV]${HEXDIG$$}+\\.${merge(UNRESERVED$$, SUB_DELIMS$$, '[\\:]')}+`);
            const IP_LITERAL$ = subexp(`\\[${subexp(`${IPV6ADDRZ_RELAXED$}|${IPV6ADDRESS$}|${IPVFUTURE$}`)}\\]`);
            // RFC 6874
            const REG_NAME$ = subexp(`${subexp(`${PCT_ENCODED$}|${merge(UNRESERVED$$, SUB_DELIMS$$)}`)}*`);
            const HOST$ = subexp(`${IP_LITERAL$}|${IPV4ADDRESS$}(?!${REG_NAME$})` + `|${REG_NAME$}`);
            const PORT$ = subexp(`${DIGIT$$}*`);
            const AUTHORITY$ = subexp(`${subexp(`${USERINFO$}@`)}?${HOST$}${subexp(`\\:${PORT$}`)}?`);
            const PCHAR$ = subexp(`${PCT_ENCODED$}|${merge(UNRESERVED$$, SUB_DELIMS$$, '[\\:\\@]')}`);
            const SEGMENT$ = subexp(`${PCHAR$}*`);
            const SEGMENT_NZ$ = subexp(`${PCHAR$}+`);
            const SEGMENT_NZ_NC$ = subexp(`${subexp(`${PCT_ENCODED$}|${merge(UNRESERVED$$, SUB_DELIMS$$, '[\\@]')}`)}+`);
            const PATH_ABEMPTY$ = subexp(`${subexp(`\\/${SEGMENT$}`)}*`);
            const PATH_ABSOLUTE$ = subexp(`\\/${subexp(SEGMENT_NZ$ + PATH_ABEMPTY$)}?`);
            // simplified
            const PATH_NOSCHEME$ = subexp(SEGMENT_NZ_NC$ + PATH_ABEMPTY$);
            // simplified
            const PATH_ROOTLESS$ = subexp(SEGMENT_NZ$ + PATH_ABEMPTY$);
            // simplified
            const PATH_EMPTY$ = `(?!${PCHAR$})`;
            const PATH$ = subexp(`${PATH_ABEMPTY$}|${PATH_ABSOLUTE$}|${PATH_NOSCHEME$}|${PATH_ROOTLESS$}|${PATH_EMPTY$}`);
            const QUERY$ = subexp(`${subexp(`${PCHAR$}|${merge('[\\/\\?]', IPRIVATE$$)}`)}*`);
            const FRAGMENT$ = subexp(`${subexp(`${PCHAR$}|[\\/\\?]`)}*`);
            const HIER_PART$ = subexp(`${subexp(`\\/\\/${AUTHORITY$}${PATH_ABEMPTY$}`)}|${PATH_ABSOLUTE$}|${PATH_ROOTLESS$}|${PATH_EMPTY$}`);
            const URI$ = subexp(`${SCHEME$}\\:${HIER_PART$}${subexp(`\\?${QUERY$}`)}?${subexp(`\\#${FRAGMENT$}`)}?`);
            const RELATIVE_PART$ = subexp(`${subexp(`\\/\\/${AUTHORITY$}${PATH_ABEMPTY$}`)}|${PATH_ABSOLUTE$}|${PATH_NOSCHEME$}|${PATH_EMPTY$}`);
            const RELATIVE$ = subexp(`${RELATIVE_PART$ + subexp(`\\?${QUERY$}`)}?${subexp(`\\#${FRAGMENT$}`)}?`);
            const URI_REFERENCE$ = subexp(`${URI$}|${RELATIVE$}`);
            const ABSOLUTE_URI$ = subexp(`${SCHEME$}\\:${HIER_PART$}${subexp(`\\?${QUERY$}`)}?`);
            const GENERIC_REF$ = `^(${SCHEME$})\\:${subexp(`${subexp(`\\/\\/(${subexp(`(${  USERINFO$  })@`)}?(${HOST$})${subexp(`\\:(${  PORT$  })`)}?)`)}?(${PATH_ABEMPTY$}|${PATH_ABSOLUTE$}|${PATH_ROOTLESS$}|${PATH_EMPTY$})`)}${subexp(`\\?(${QUERY$})`)}?${subexp(`\\#(${FRAGMENT$})`)}?$`;
            const RELATIVE_REF$ = `^(){0}${subexp(`${subexp(`\\/\\/(${subexp(`(${  USERINFO$  })@`)}?(${HOST$})${subexp(`\\:(${  PORT$  })`)}?)`)}?(${PATH_ABEMPTY$}|${PATH_ABSOLUTE$}|${PATH_NOSCHEME$}|${PATH_EMPTY$})`)}${subexp(`\\?(${QUERY$})`)}?${subexp(`\\#(${FRAGMENT$})`)}?$`;
            const ABSOLUTE_REF$ = `^(${SCHEME$})\\:${subexp(`${subexp(`\\/\\/(${subexp(`(${  USERINFO$  })@`)}?(${HOST$})${subexp(`\\:(${  PORT$  })`)}?)`)}?(${PATH_ABEMPTY$}|${PATH_ABSOLUTE$}|${PATH_ROOTLESS$}|${PATH_EMPTY$})`)}${subexp(`\\?(${QUERY$})`)}?$`;
            const SAMEDOC_REF$ = `^${subexp(`\\#(${FRAGMENT$})`)}?$`;
            const AUTHORITY_REF$ = `^${subexp(`(${USERINFO$})@`)}?(${HOST$})${subexp(`\\:(${PORT$})`)}?$`;
            return {
              NOT_SCHEME: new RegExp(merge('[^]', ALPHA$$, DIGIT$$, '[\\+\\-\\.]'), 'g'),
              NOT_USERINFO: new RegExp(merge('[^\\%\\:]', UNRESERVED$$, SUB_DELIMS$$), 'g'),
              NOT_HOST: new RegExp(merge('[^\\%\\[\\]\\:]', UNRESERVED$$, SUB_DELIMS$$), 'g'),
              NOT_PATH: new RegExp(merge('[^\\%\\/\\:\\@]', UNRESERVED$$, SUB_DELIMS$$), 'g'),
              NOT_PATH_NOSCHEME: new RegExp(merge('[^\\%\\/\\@]', UNRESERVED$$, SUB_DELIMS$$), 'g'),
              NOT_QUERY: new RegExp(merge('[^\\%]', UNRESERVED$$, SUB_DELIMS$$, '[\\:\\@\\/\\?]', IPRIVATE$$), 'g'),
              NOT_FRAGMENT: new RegExp(merge('[^\\%]', UNRESERVED$$, SUB_DELIMS$$, '[\\:\\@\\/\\?]'), 'g'),
              ESCAPE: new RegExp(merge('[^]', UNRESERVED$$, SUB_DELIMS$$), 'g'),
              UNRESERVED: new RegExp(UNRESERVED$$, 'g'),
              OTHER_CHARS: new RegExp(merge('[^\\%]', UNRESERVED$$, RESERVED$$), 'g'),
              PCT_ENCODED: new RegExp(PCT_ENCODED$, 'g'),
              IPV4ADDRESS: new RegExp(`^(${IPV4ADDRESS$})$`),
              IPV6ADDRESS: new RegExp(`^\\[?(${IPV6ADDRESS$})${subexp(`${subexp(`\\%25|\\%(?!${HEXDIG$$}{2})`)}(${ZONEID$})`)}?\\]?$`), // RFC 6874, with relaxed parsing rules
            };
          }
          const URI_PROTOCOL = buildExps(false);

          const IRI_PROTOCOL = buildExps(true);

          const slicedToArray = (function () {
            function sliceIterator(arr, i) {
              const _arr = [];
              let _n = true;
              let _d = false;
              let _e = undefined;

              try {
                for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) {
                  _arr.push(_s.value);

                  if (i && _arr.length === i) break;
                }
              } catch (err) {
                _d = true;
                _e = err;
              } finally {
                try {
                  if (!_n && _i.return) _i.return();
                } finally {
                  if (_d) throw _e;
                }
              }

              return _arr;
            }

            return function (arr, i) {
              if (Array.isArray(arr)) {
                return arr;
              } if (Symbol.iterator in Object(arr)) {
                return sliceIterator(arr, i);
              }
              throw new TypeError('Invalid attempt to destructure non-iterable instance');
            };
          }());


          const toConsumableArray = function (arr) {
            if (Array.isArray(arr)) {
              for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) arr2[i] = arr[i];

              return arr2;
            }
            return Array.from(arr);
          };

          /** Highest positive signed 32-bit float value */

          const maxInt = 2147483647; // aka. 0x7FFFFFFF or 2^31-1

          /** Bootstring parameters */
          const base = 36;
          const tMin = 1;
          const tMax = 26;
          const skew = 38;
          const damp = 700;
          const initialBias = 72;
          const initialN = 128; // 0x80
          const delimiter = '-'; // '\x2D'

          /** Regular expressions */
          const regexPunycode = /^xn--/;
          const regexNonASCII = /[^\0-\x7E]/; // non-ASCII chars
          const regexSeparators = /[\x2E\u3002\uFF0E\uFF61]/g; // RFC 3490 separators

          /** Error messages */
          const errors = {
            overflow: 'Overflow: input needs wider integers to process',
            'not-basic': 'Illegal input >= 0x80 (not a basic code point)',
            'invalid-input': 'Invalid input',
          };

          /** Convenience shortcuts */
          const baseMinusTMin = base - tMin;
          const { floor } = Math;
          const stringFromCharCode = String.fromCharCode;

          /* --------------------------------------------------------------------------*/

          /**
 * A generic error utility function.
 * @private
 * @param {String} type The error type.
 * @returns {Error} Throws a `RangeError` with the applicable error message.
 */
          function error$1(type) {
            throw new RangeError(errors[type]);
          }

          /**
 * A generic `Array#map` utility function.
 * @private
 * @param {Array} array The array to iterate over.
 * @param {Function} callback The function that gets called for every array
 * item.
 * @returns {Array} A new array of values returned by the callback function.
 */
          function map(array, fn) {
            const result = [];
            let { length } = array;
            while (length--) {
              result[length] = fn(array[length]);
            }
            return result;
          }

          /**
 * A simple `Array#map`-like wrapper to work with domain name strings or email
 * addresses.
 * @private
 * @param {String} domain The domain name or email address.
 * @param {Function} callback The function that gets called for every
 * character.
 * @returns {Array} A new string of characters returned by the callback
 * function.
 */
          function mapDomain(string, fn) {
            const parts = string.split('@');
            let result = '';
            if (parts.length > 1) {
              // In email addresses, only the domain name should be punycoded. Leave
              // the local part (i.e. everything up to `@`) intact.
              result = `${parts[0]}@`;
              string = parts[1];
            }
            // Avoid `split(regex)` for IE8 compatibility. See #17.
            string = string.replace(regexSeparators, '\x2E');
            const labels = string.split('.');
            const encoded = map(labels, fn).join('.');
            return result + encoded;
          }

          /**
 * Creates an array containing the numeric code points of each Unicode
 * character in the string. While JavaScript uses UCS-2 internally,
 * this function will convert a pair of surrogate halves (each of which
 * UCS-2 exposes as separate characters) into a single code point,
 * matching UTF-16.
 * @see `punycode.ucs2.encode`
 * @see <https://mathiasbynens.be/notes/javascript-encoding>
 * @memberOf punycode.ucs2
 * @name decode
 * @param {String} string The Unicode input string (UCS-2).
 * @returns {Array} The new array of code points.
 */
          function ucs2decode(string) {
            const output = [];
            let counter = 0;
            const { length } = string;
            while (counter < length) {
              const value = string.charCodeAt(counter++);
              if (value >= 0xD800 && value <= 0xDBFF && counter < length) {
                // It's a high surrogate, and there is a next character.
                const extra = string.charCodeAt(counter++);
                if ((extra & 0xFC00) == 0xDC00) {
                  // Low surrogate.
                  output.push(((value & 0x3FF) << 10) + (extra & 0x3FF) + 0x10000);
                } else {
                  // It's an unmatched surrogate; only append this code unit, in case the
                  // next code unit is the high surrogate of a surrogate pair.
                  output.push(value);
                  counter--;
                }
              } else {
                output.push(value);
              }
            }
            return output;
          }

          /**
 * Creates a string based on an array of numeric code points.
 * @see `punycode.ucs2.decode`
 * @memberOf punycode.ucs2
 * @name encode
 * @param {Array} codePoints The array of numeric code points.
 * @returns {String} The new Unicode string (UCS-2).
 */
          const ucs2encode = function ucs2encode(array) {
            return String.fromCodePoint.apply(String, toConsumableArray(array));
          };

          /**
 * Converts a basic code point into a digit/integer.
 * @see `digitToBasic()`
 * @private
 * @param {Number} codePoint The basic numeric code point value.
 * @returns {Number} The numeric value of a basic code point (for use in
 * representing integers) in the range `0` to `base - 1`, or `base` if
 * the code point does not represent a value.
 */
          const basicToDigit = function basicToDigit(codePoint) {
            if (codePoint - 0x30 < 0x0A) {
              return codePoint - 0x16;
            }
            if (codePoint - 0x41 < 0x1A) {
              return codePoint - 0x41;
            }
            if (codePoint - 0x61 < 0x1A) {
              return codePoint - 0x61;
            }
            return base;
          };

          /**
 * Converts a digit/integer into a basic code point.
 * @see `basicToDigit()`
 * @private
 * @param {Number} digit The numeric value of a basic code point.
 * @returns {Number} The basic code point whose value (when used for
 * representing integers) is `digit`, which needs to be in the range
 * `0` to `base - 1`. If `flag` is non-zero, the uppercase form is
 * used; else, the lowercase form is used. The behavior is undefined
 * if `flag` is non-zero and `digit` has no uppercase form.
 */
          const digitToBasic = function digitToBasic(digit, flag) {
            //  0..25 map to ASCII a..z or A..Z
            // 26..35 map to ASCII 0..9
            return digit + 22 + 75 * (digit < 26) - ((flag != 0) << 5);
          };

          /**
 * Bias adaptation function as per section 3.4 of RFC 3492.
 * https://tools.ietf.org/html/rfc3492#section-3.4
 * @private
 */
          const adapt = function adapt(delta, numPoints, firstTime) {
            let k = 0;
            delta = firstTime ? floor(delta / damp) : delta >> 1;
            delta += floor(delta / numPoints);
            for (; /* no initialization */delta > baseMinusTMin * tMax >> 1; k += base) {
              delta = floor(delta / baseMinusTMin);
            }
            return floor(k + (baseMinusTMin + 1) * delta / (delta + skew));
          };

          /**
 * Converts a Punycode string of ASCII-only symbols to a string of Unicode
 * symbols.
 * @memberOf punycode
 * @param {String} input The Punycode string of ASCII-only symbols.
 * @returns {String} The resulting string of Unicode symbols.
 */
          const decode = function decode(input) {
            // Don't use UCS-2.
            const output = [];
            const inputLength = input.length;
            let i = 0;
            let n = initialN;
            let bias = initialBias;

            // Handle the basic code points: let `basic` be the number of input code
            // points before the last delimiter, or `0` if there is none, then copy
            // the first basic code points to the output.

            let basic = input.lastIndexOf(delimiter);
            if (basic < 0) {
              basic = 0;
            }

            for (let j = 0; j < basic; ++j) {
              // if it's not a basic code point
              if (input.charCodeAt(j) >= 0x80) {
                error$1('not-basic');
              }
              output.push(input.charCodeAt(j));
            }

            // Main decoding loop: start just after the last delimiter if any basic code
            // points were copied; start at the beginning otherwise.

            for (let index = basic > 0 ? basic + 1 : 0; index < inputLength;) /* no final expression */{
              // `index` is the index of the next character to be consumed.
              // Decode a generalized variable-length integer into `delta`,
              // which gets added to `i`. The overflow checking is easier
              // if we increase `i` as we go, then subtract off its starting
              // value at the end to obtain `delta`.
              const oldi = i;
              for (let w = 1, k = base;; /* no condition */k += base) {
                if (index >= inputLength) {
                  error$1('invalid-input');
                }

                const digit = basicToDigit(input.charCodeAt(index++));

                if (digit >= base || digit > floor((maxInt - i) / w)) {
                  error$1('overflow');
                }

                i += digit * w;
                const t = k <= bias ? tMin : k >= bias + tMax ? tMax : k - bias;

                if (digit < t) {
                  break;
                }

                const baseMinusT = base - t;
                if (w > floor(maxInt / baseMinusT)) {
                  error$1('overflow');
                }

                w *= baseMinusT;
              }

              const out = output.length + 1;
              bias = adapt(i - oldi, out, oldi == 0);

              // `i` was supposed to wrap around from `out` to `0`,
              // incrementing `n` each time, so we'll fix that now:
              if (floor(i / out) > maxInt - n) {
                error$1('overflow');
              }

              n += floor(i / out);
              i %= out;

              // Insert `n` at position `i` of the output.
              output.splice(i++, 0, n);
            }

            return String.fromCodePoint.apply(String, output);
          };

          /**
 * Converts a string of Unicode symbols (e.g. a domain name label) to a
 * Punycode string of ASCII-only symbols.
 * @memberOf punycode
 * @param {String} input The string of Unicode symbols.
 * @returns {String} The resulting Punycode string of ASCII-only symbols.
 */
          const encode = function encode(input) {
            const output = [];

            // Convert the input in UCS-2 to an array of Unicode code points.
            input = ucs2decode(input);

            // Cache the length.
            const inputLength = input.length;

            // Initialize the state.
            let n = initialN;
            let delta = 0;
            let bias = initialBias;

            // Handle the basic code points.
            let _iteratorNormalCompletion = true;
            let _didIteratorError = false;
            let _iteratorError = undefined;

            try {
              for (var _iterator = input[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                const _currentValue2 = _step.value;

                if (_currentValue2 < 0x80) {
                  output.push(stringFromCharCode(_currentValue2));
                }
              }
            } catch (err) {
              _didIteratorError = true;
              _iteratorError = err;
            } finally {
              try {
                if (!_iteratorNormalCompletion && _iterator.return) {
                  _iterator.return();
                }
              } finally {
                if (_didIteratorError) {
                  throw _iteratorError;
                }
              }
            }

            const basicLength = output.length;
            let handledCPCount = basicLength;

            // `handledCPCount` is the number of code points that have been handled;
            // `basicLength` is the number of basic code points.

            // Finish the basic string with a delimiter unless it's empty.
            if (basicLength) {
              output.push(delimiter);
            }

            // Main encoding loop:
            while (handledCPCount < inputLength) {
              // All non-basic code points < n have been handled already. Find the next
              // larger one:
              let m = maxInt;
              let _iteratorNormalCompletion2 = true;
              let _didIteratorError2 = false;
              let _iteratorError2 = undefined;

              try {
                for (var _iterator2 = input[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                  const currentValue = _step2.value;

                  if (currentValue >= n && currentValue < m) {
                    m = currentValue;
                  }
                }

                // Increase `delta` enough to advance the decoder's <n,i> state to <m,0>,
                // but guard against overflow.
              } catch (err) {
                _didIteratorError2 = true;
                _iteratorError2 = err;
              } finally {
                try {
                  if (!_iteratorNormalCompletion2 && _iterator2.return) {
                    _iterator2.return();
                  }
                } finally {
                  if (_didIteratorError2) {
                    throw _iteratorError2;
                  }
                }
              }

              const handledCPCountPlusOne = handledCPCount + 1;
              if (m - n > floor((maxInt - delta) / handledCPCountPlusOne)) {
                error$1('overflow');
              }

              delta += (m - n) * handledCPCountPlusOne;
              n = m;

              let _iteratorNormalCompletion3 = true;
              let _didIteratorError3 = false;
              let _iteratorError3 = undefined;

              try {
                for (var _iterator3 = input[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
                  const _currentValue = _step3.value;

                  if (_currentValue < n && ++delta > maxInt) {
                    error$1('overflow');
                  }
                  if (_currentValue == n) {
                    // Represent delta as a generalized variable-length integer.
                    let q = delta;
                    for (let k = base;; /* no condition */k += base) {
                      const t = k <= bias ? tMin : k >= bias + tMax ? tMax : k - bias;
                      if (q < t) {
                        break;
                      }
                      const qMinusT = q - t;
                      const baseMinusT = base - t;
                      output.push(stringFromCharCode(digitToBasic(t + qMinusT % baseMinusT, 0)));
                      q = floor(qMinusT / baseMinusT);
                    }

                    output.push(stringFromCharCode(digitToBasic(q, 0)));
                    bias = adapt(delta, handledCPCountPlusOne, handledCPCount == basicLength);
                    delta = 0;
                    ++handledCPCount;
                  }
                }
              } catch (err) {
                _didIteratorError3 = true;
                _iteratorError3 = err;
              } finally {
                try {
                  if (!_iteratorNormalCompletion3 && _iterator3.return) {
                    _iterator3.return();
                  }
                } finally {
                  if (_didIteratorError3) {
                    throw _iteratorError3;
                  }
                }
              }

              ++delta;
              ++n;
            }
            return output.join('');
          };

          /**
 * Converts a Punycode string representing a domain name or an email address
 * to Unicode. Only the Punycoded parts of the input will be converted, i.e.
 * it doesn't matter if you call it on a string that has already been
 * converted to Unicode.
 * @memberOf punycode
 * @param {String} input The Punycoded domain name or email address to
 * convert to Unicode.
 * @returns {String} The Unicode representation of the given Punycode
 * string.
 */
          const toUnicode = function toUnicode(input) {
            return mapDomain(input, string => (regexPunycode.test(string) ? decode(string.slice(4).toLowerCase()) : string));
          };

          /**
 * Converts a Unicode string representing a domain name or an email address to
 * Punycode. Only the non-ASCII parts of the domain name will be converted,
 * i.e. it doesn't matter if you call it with a domain that's already in
 * ASCII.
 * @memberOf punycode
 * @param {String} input The domain name or email address to convert, as a
 * Unicode string.
 * @returns {String} The Punycode representation of the given domain name or
 * email address.
 */
          const toASCII = function toASCII(input) {
            return mapDomain(input, string => (regexNonASCII.test(string) ? `xn--${encode(string)}` : string));
          };

          /* --------------------------------------------------------------------------*/

          /** Define the public API */
          const punycode = {
            /**
  * A string representing the current Punycode.js version number.
  * @memberOf punycode
  * @type String
  */
            version: '2.1.0',
            /**
  * An object of methods to convert from JavaScript's internal character
  * representation (UCS-2) to Unicode code points, and back.
  * @see <https://mathiasbynens.be/notes/javascript-encoding>
  * @memberOf punycode
  * @type Object
  */
            ucs2: {
              decode: ucs2decode,
              encode: ucs2encode,
            },
            decode,
            encode,
            toASCII,
            toUnicode,
          };

          /**
 * URI.js
 *
 * @fileoverview An RFC 3986 compliant, scheme extendable URI parsing/validating/resolving library for JavaScript.
 * @author <a href="mailto:gary.court@gmail.com">Gary Court</a>
 * @see http://github.com/garycourt/uri-js
 */
          /**
 * Copyright 2011 Gary Court. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 *
 *    1. Redistributions of source code must retain the above copyright notice, this list of
 *       conditions and the following disclaimer.
 *
 *    2. Redistributions in binary form must reproduce the above copyright notice, this list
 *       of conditions and the following disclaimer in the documentation and/or other materials
 *       provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY GARY COURT ``AS IS'' AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GARY COURT OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * The views and conclusions contained in the software and documentation are those of the
 * authors and should not be interpreted as representing official policies, either expressed
 * or implied, of Gary Court.
 */
          const SCHEMES = {};
          function pctEncChar(chr) {
            const c = chr.charCodeAt(0);
            let e = void 0;
            if (c < 16) e = `%0${c.toString(16).toUpperCase()}`;else if (c < 128) e = `%${c.toString(16).toUpperCase()}`;else if (c < 2048) e = `%${(c >> 6 | 192).toString(16).toUpperCase()}%${(c & 63 | 128).toString(16).toUpperCase()}`;else e = `%${(c >> 12 | 224).toString(16).toUpperCase()}%${(c >> 6 & 63 | 128).toString(16).toUpperCase()}%${(c & 63 | 128).toString(16).toUpperCase()}`;
            return e;
          }
          function pctDecChars(str) {
            let newStr = '';
            let i = 0;
            const il = str.length;
            while (i < il) {
              const c = parseInt(str.substr(i + 1, 2), 16);
              if (c < 128) {
                newStr += String.fromCharCode(c);
                i += 3;
              } else if (c >= 194 && c < 224) {
                if (il - i >= 6) {
                  const c2 = parseInt(str.substr(i + 4, 2), 16);
                  newStr += String.fromCharCode((c & 31) << 6 | c2 & 63);
                } else {
                  newStr += str.substr(i, 6);
                }
                i += 6;
              } else if (c >= 224) {
                if (il - i >= 9) {
                  const _c = parseInt(str.substr(i + 4, 2), 16);
                  const c3 = parseInt(str.substr(i + 7, 2), 16);
                  newStr += String.fromCharCode((c & 15) << 12 | (_c & 63) << 6 | c3 & 63);
                } else {
                  newStr += str.substr(i, 9);
                }
                i += 9;
              } else {
                newStr += str.substr(i, 3);
                i += 3;
              }
            }
            return newStr;
          }
          function _normalizeComponentEncoding(components, protocol) {
            function decodeUnreserved(str) {
              const decStr = pctDecChars(str);
              return !decStr.match(protocol.UNRESERVED) ? str : decStr;
            }
            if (components.scheme) components.scheme = String(components.scheme).replace(protocol.PCT_ENCODED, decodeUnreserved)
              .toLowerCase()
              .replace(protocol.NOT_SCHEME, '');
            if (components.userinfo !== undefined) components.userinfo = String(components.userinfo).replace(protocol.PCT_ENCODED, decodeUnreserved)
              .replace(protocol.NOT_USERINFO, pctEncChar)
              .replace(protocol.PCT_ENCODED, toUpperCase);
            if (components.host !== undefined) components.host = String(components.host).replace(protocol.PCT_ENCODED, decodeUnreserved)
              .toLowerCase()
              .replace(protocol.NOT_HOST, pctEncChar)
              .replace(protocol.PCT_ENCODED, toUpperCase);
            if (components.path !== undefined) components.path = String(components.path).replace(protocol.PCT_ENCODED, decodeUnreserved)
              .replace(components.scheme ? protocol.NOT_PATH : protocol.NOT_PATH_NOSCHEME, pctEncChar)
              .replace(protocol.PCT_ENCODED, toUpperCase);
            if (components.query !== undefined) components.query = String(components.query).replace(protocol.PCT_ENCODED, decodeUnreserved)
              .replace(protocol.NOT_QUERY, pctEncChar)
              .replace(protocol.PCT_ENCODED, toUpperCase);
            if (components.fragment !== undefined) components.fragment = String(components.fragment).replace(protocol.PCT_ENCODED, decodeUnreserved)
              .replace(protocol.NOT_FRAGMENT, pctEncChar)
              .replace(protocol.PCT_ENCODED, toUpperCase);
            return components;
          }

          function _stripLeadingZeros(str) {
            return str.replace(/^0*(.*)/, '$1') || '0';
          }
          function _normalizeIPv4(host, protocol) {
            const matches = host.match(protocol.IPV4ADDRESS) || [];

            const _matches = slicedToArray(matches, 2);
            const address = _matches[1];

            if (address) {
              return address.split('.').map(_stripLeadingZeros)
                .join('.');
            }
            return host;
          }
          function _normalizeIPv6(host, protocol) {
            const matches = host.match(protocol.IPV6ADDRESS) || [];

            const _matches2 = slicedToArray(matches, 3);
            const address = _matches2[1];
            const zone = _matches2[2];

            if (address) {
              const _address$toLowerCase$ = address.toLowerCase().split('::')
                .reverse();
              const _address$toLowerCase$2 = slicedToArray(_address$toLowerCase$, 2);
              const last = _address$toLowerCase$2[0];
              const first = _address$toLowerCase$2[1];

              const firstFields = first ? first.split(':').map(_stripLeadingZeros) : [];
              const lastFields = last.split(':').map(_stripLeadingZeros);
              const isLastFieldIPv4Address = protocol.IPV4ADDRESS.test(lastFields[lastFields.length - 1]);
              const fieldCount = isLastFieldIPv4Address ? 7 : 8;
              const lastFieldsStart = lastFields.length - fieldCount;
              const fields = Array(fieldCount);
              for (let x = 0; x < fieldCount; ++x) {
                fields[x] = firstFields[x] || lastFields[lastFieldsStart + x] || '';
              }
              if (isLastFieldIPv4Address) {
                fields[fieldCount - 1] = _normalizeIPv4(fields[fieldCount - 1], protocol);
              }
              const allZeroFields = fields.reduce((acc, field, index) => {
                if (!field || field === '0') {
                  const lastLongest = acc[acc.length - 1];
                  if (lastLongest && lastLongest.index + lastLongest.length === index) {
                    lastLongest.length++;
                  } else {
                    acc.push({ index, length: 1 });
                  }
                }
                return acc;
              }, []);
              const longestZeroFields = allZeroFields.sort((a, b) => b.length - a.length)[0];
              let newHost = void 0;
              if (longestZeroFields && longestZeroFields.length > 1) {
                const newFirst = fields.slice(0, longestZeroFields.index);
                const newLast = fields.slice(longestZeroFields.index + longestZeroFields.length);
                newHost = `${newFirst.join(':')}::${newLast.join(':')}`;
              } else {
                newHost = fields.join(':');
              }
              if (zone) {
                newHost += `%${zone}`;
              }
              return newHost;
            }
            return host;
          }
          const URI_PARSE = /^(?:([^:\/?#]+):)?(?:\/\/((?:([^\/?#@]*)@)?(\[[^\/?#\]]+\]|[^\/?#:]*)(?:\:(\d*))?))?([^?#]*)(?:\?([^#]*))?(?:#((?:.|\n|\r)*))?/i;
          const NO_MATCH_IS_UNDEFINED = ''.match(/(){0}/)[1] === undefined;
          function parse(uriString) {
            const options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

            const components = {};
            const protocol = options.iri !== false ? IRI_PROTOCOL : URI_PROTOCOL;
            if (options.reference === 'suffix') uriString = `${options.scheme ? `${options.scheme}:` : ''}//${uriString}`;
            const matches = uriString.match(URI_PARSE);
            if (matches) {
              if (NO_MATCH_IS_UNDEFINED) {
                // store each component
                components.scheme = matches[1];
                components.userinfo = matches[3];
                components.host = matches[4];
                components.port = parseInt(matches[5], 10);
                components.path = matches[6] || '';
                components.query = matches[7];
                components.fragment = matches[8];
                // fix port number
                if (isNaN(components.port)) {
                  components.port = matches[5];
                }
              } else {
                // IE FIX for improper RegExp matching
                // store each component
                components.scheme = matches[1] || undefined;
                components.userinfo = uriString.indexOf('@') !== -1 ? matches[3] : undefined;
                components.host = uriString.indexOf('//') !== -1 ? matches[4] : undefined;
                components.port = parseInt(matches[5], 10);
                components.path = matches[6] || '';
                components.query = uriString.indexOf('?') !== -1 ? matches[7] : undefined;
                components.fragment = uriString.indexOf('#') !== -1 ? matches[8] : undefined;
                // fix port number
                if (isNaN(components.port)) {
                  components.port = uriString.match(/\/\/(?:.|\n)*\:(?:\/|\?|\#|$)/) ? matches[4] : undefined;
                }
              }
              if (components.host) {
                // normalize IP hosts
                components.host = _normalizeIPv6(_normalizeIPv4(components.host, protocol), protocol);
              }
              // determine reference type
              if (components.scheme === undefined && components.userinfo === undefined && components.host === undefined && components.port === undefined && !components.path && components.query === undefined) {
                components.reference = 'same-document';
              } else if (components.scheme === undefined) {
                components.reference = 'relative';
              } else if (components.fragment === undefined) {
                components.reference = 'absolute';
              } else {
                components.reference = 'uri';
              }
              // check for reference errors
              if (options.reference && options.reference !== 'suffix' && options.reference !== components.reference) {
                components.error = components.error || `URI is not a ${options.reference} reference.`;
              }
              // find scheme handler
              const schemeHandler = SCHEMES[(options.scheme || components.scheme || '').toLowerCase()];
              // check if scheme can't handle IRIs
              if (!options.unicodeSupport && (!schemeHandler || !schemeHandler.unicodeSupport)) {
                // if host component is a domain name
                if (components.host && (options.domainHost || schemeHandler && schemeHandler.domainHost)) {
                // convert Unicode IDN -> ASCII IDN
                  try {
                    components.host = punycode.toASCII(components.host.replace(protocol.PCT_ENCODED, pctDecChars).toLowerCase());
                  } catch (e) {
                    components.error = components.error || `Host's domain name can not be converted to ASCII via punycode: ${e}`;
                  }
                }
                // convert IRI -> URI
                _normalizeComponentEncoding(components, URI_PROTOCOL);
              } else {
                // normalize encodings
                _normalizeComponentEncoding(components, protocol);
              }
              // perform scheme specific parsing
              if (schemeHandler && schemeHandler.parse) {
                schemeHandler.parse(components, options);
              }
            } else {
              components.error = components.error || 'URI can not be parsed.';
            }
            return components;
          }

          function _recomposeAuthority(components, options) {
            const protocol = options.iri !== false ? IRI_PROTOCOL : URI_PROTOCOL;
            const uriTokens = [];
            if (components.userinfo !== undefined) {
              uriTokens.push(components.userinfo);
              uriTokens.push('@');
            }
            if (components.host !== undefined) {
              // normalize IP hosts, add brackets and escape zone separator for IPv6
              uriTokens.push(_normalizeIPv6(_normalizeIPv4(String(components.host), protocol), protocol).replace(protocol.IPV6ADDRESS, (_, $1, $2) => `[${$1}${$2 ? `%25${$2}` : ''}]`));
            }
            if (typeof components.port === 'number' || typeof components.port === 'string') {
              uriTokens.push(':');
              uriTokens.push(String(components.port));
            }
            return uriTokens.length ? uriTokens.join('') : undefined;
          }

          const RDS1 = /^\.\.?\//;
          const RDS2 = /^\/\.(\/|$)/;
          const RDS3 = /^\/\.\.(\/|$)/;
          const RDS5 = /^\/?(?:.|\n)*?(?=\/|$)/;
          function removeDotSegments(input) {
            const output = [];
            while (input.length) {
              if (input.match(RDS1)) {
                input = input.replace(RDS1, '');
              } else if (input.match(RDS2)) {
                input = input.replace(RDS2, '/');
              } else if (input.match(RDS3)) {
                input = input.replace(RDS3, '/');
                output.pop();
              } else if (input === '.' || input === '..') {
                input = '';
              } else {
                const im = input.match(RDS5);
                if (im) {
                  const s = im[0];
                  input = input.slice(s.length);
                  output.push(s);
                } else {
                  throw new Error('Unexpected dot segment condition');
                }
              }
            }
            return output.join('');
          }

          function serialize(components) {
            const options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

            const protocol = options.iri ? IRI_PROTOCOL : URI_PROTOCOL;
            const uriTokens = [];
            // find scheme handler
            const schemeHandler = SCHEMES[(options.scheme || components.scheme || '').toLowerCase()];
            // perform scheme specific serialization
            if (schemeHandler && schemeHandler.serialize) schemeHandler.serialize(components, options);
            if (components.host) {
              // if host component is an IPv6 address
              if (protocol.IPV6ADDRESS.test(components.host)) {}
              // TODO: normalize IPv6 address as per RFC 5952

              // if host component is a domain name
              else if (options.domainHost || schemeHandler && schemeHandler.domainHost) {
                // convert IDN via punycode
                try {
                  components.host = !options.iri ? punycode.toASCII(components.host.replace(protocol.PCT_ENCODED, pctDecChars).toLowerCase()) : punycode.toUnicode(components.host);
                } catch (e) {
                  components.error = components.error || `Host's domain name can not be converted to ${!options.iri ? 'ASCII' : 'Unicode'} via punycode: ${e}`;
                }
              }
            }
            // normalize encoding
            _normalizeComponentEncoding(components, protocol);
            if (options.reference !== 'suffix' && components.scheme) {
              uriTokens.push(components.scheme);
              uriTokens.push(':');
            }
            const authority = _recomposeAuthority(components, options);
            if (authority !== undefined) {
              if (options.reference !== 'suffix') {
                uriTokens.push('//');
              }
              uriTokens.push(authority);
              if (components.path && components.path.charAt(0) !== '/') {
                uriTokens.push('/');
              }
            }
            if (components.path !== undefined) {
              let s = components.path;
              if (!options.absolutePath && (!schemeHandler || !schemeHandler.absolutePath)) {
                s = removeDotSegments(s);
              }
              if (authority === undefined) {
                s = s.replace(/^\/\//, '/%2F'); // don't allow the path to start with "//"
              }
              uriTokens.push(s);
            }
            if (components.query !== undefined) {
              uriTokens.push('?');
              uriTokens.push(components.query);
            }
            if (components.fragment !== undefined) {
              uriTokens.push('#');
              uriTokens.push(components.fragment);
            }
            return uriTokens.join(''); // merge tokens into a string
          }

          function resolveComponents(base, relative) {
            let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
            const skipNormalization = arguments[3];

            const target = {};
            if (!skipNormalization) {
              base = parse(serialize(base, options), options); // normalize base components
              relative = parse(serialize(relative, options), options); // normalize relative components
            }
            options = options || {};
            if (!options.tolerant && relative.scheme) {
              target.scheme = relative.scheme;
              // target.authority = relative.authority;
              target.userinfo = relative.userinfo;
              target.host = relative.host;
              target.port = relative.port;
              target.path = removeDotSegments(relative.path || '');
              target.query = relative.query;
            } else {
              if (relative.userinfo !== undefined || relative.host !== undefined || relative.port !== undefined) {
                // target.authority = relative.authority;
                target.userinfo = relative.userinfo;
                target.host = relative.host;
                target.port = relative.port;
                target.path = removeDotSegments(relative.path || '');
                target.query = relative.query;
              } else {
                if (!relative.path) {
                  target.path = base.path;
                  if (relative.query !== undefined) {
                    target.query = relative.query;
                  } else {
                    target.query = base.query;
                  }
                } else {
                  if (relative.path.charAt(0) === '/') {
                    target.path = removeDotSegments(relative.path);
                  } else {
                    if ((base.userinfo !== undefined || base.host !== undefined || base.port !== undefined) && !base.path) {
                      target.path = `/${relative.path}`;
                    } else if (!base.path) {
                      target.path = relative.path;
                    } else {
                      target.path = base.path.slice(0, base.path.lastIndexOf('/') + 1) + relative.path;
                    }
                    target.path = removeDotSegments(target.path);
                  }
                  target.query = relative.query;
                }
                // target.authority = base.authority;
                target.userinfo = base.userinfo;
                target.host = base.host;
                target.port = base.port;
              }
              target.scheme = base.scheme;
            }
            target.fragment = relative.fragment;
            return target;
          }

          function resolve(baseURI, relativeURI, options) {
            const schemelessOptions = assign({ scheme: 'null' }, options);
            return serialize(resolveComponents(parse(baseURI, schemelessOptions), parse(relativeURI, schemelessOptions), schemelessOptions, true), schemelessOptions);
          }

          function normalize(uri, options) {
            if (typeof uri === 'string') {
              uri = serialize(parse(uri, options), options);
            } else if (typeOf(uri) === 'object') {
              uri = parse(serialize(uri, options), options);
            }
            return uri;
          }

          function equal(uriA, uriB, options) {
            if (typeof uriA === 'string') {
              uriA = serialize(parse(uriA, options), options);
            } else if (typeOf(uriA) === 'object') {
              uriA = serialize(uriA, options);
            }
            if (typeof uriB === 'string') {
              uriB = serialize(parse(uriB, options), options);
            } else if (typeOf(uriB) === 'object') {
              uriB = serialize(uriB, options);
            }
            return uriA === uriB;
          }

          function escapeComponent(str, options) {
            return str && str.toString().replace(!options || !options.iri ? URI_PROTOCOL.ESCAPE : IRI_PROTOCOL.ESCAPE, pctEncChar);
          }

          function unescapeComponent(str, options) {
            return str && str.toString().replace(!options || !options.iri ? URI_PROTOCOL.PCT_ENCODED : IRI_PROTOCOL.PCT_ENCODED, pctDecChars);
          }

          const handler = {
            scheme: 'http',
            domainHost: true,
            parse: function parse(components, options) {
              // report missing host
              if (!components.host) {
                components.error = components.error || 'HTTP URIs must have a host.';
              }
              return components;
            },
            serialize: function serialize(components, options) {
              const secure = String(components.scheme).toLowerCase() === 'https';
              // normalize the default port
              if (components.port === (secure ? 443 : 80) || components.port === '') {
                components.port = undefined;
              }
              // normalize the empty path
              if (!components.path) {
                components.path = '/';
              }
              // NOTE: We do not parse query strings for HTTP URIs
              // as WWW Form Url Encoded query strings are part of the HTML4+ spec,
              // and not the HTTP spec.
              return components;
            },
          };

          const handler$1 = {
            scheme: 'https',
            domainHost: handler.domainHost,
            parse: handler.parse,
            serialize: handler.serialize,
          };

          function isSecure(wsComponents) {
            return typeof wsComponents.secure === 'boolean' ? wsComponents.secure : String(wsComponents.scheme).toLowerCase() === 'wss';
          }
          // RFC 6455
          const handler$2 = {
            scheme: 'ws',
            domainHost: true,
            parse: function parse(components, options) {
              const wsComponents = components;
              // indicate if the secure flag is set
              wsComponents.secure = isSecure(wsComponents);
              // construct resouce name
              wsComponents.resourceName = (wsComponents.path || '/') + (wsComponents.query ? `?${wsComponents.query}` : '');
              wsComponents.path = undefined;
              wsComponents.query = undefined;
              return wsComponents;
            },
            serialize: function serialize(wsComponents, options) {
              // normalize the default port
              if (wsComponents.port === (isSecure(wsComponents) ? 443 : 80) || wsComponents.port === '') {
                wsComponents.port = undefined;
              }
              // ensure scheme matches secure flag
              if (typeof wsComponents.secure === 'boolean') {
                wsComponents.scheme = wsComponents.secure ? 'wss' : 'ws';
                wsComponents.secure = undefined;
              }
              // reconstruct path from resource name
              if (wsComponents.resourceName) {
                const _wsComponents$resourc = wsComponents.resourceName.split('?');
                const _wsComponents$resourc2 = slicedToArray(_wsComponents$resourc, 2);
                const path = _wsComponents$resourc2[0];
                const query = _wsComponents$resourc2[1];

                wsComponents.path = path && path !== '/' ? path : undefined;
                wsComponents.query = query;
                wsComponents.resourceName = undefined;
              }
              // forbid fragment component
              wsComponents.fragment = undefined;
              return wsComponents;
            },
          };

          const handler$3 = {
            scheme: 'wss',
            domainHost: handler$2.domainHost,
            parse: handler$2.parse,
            serialize: handler$2.serialize,
          };

          const O = {};
          const isIRI = true;
          // RFC 3986
          const UNRESERVED$$ = `[A-Za-z0-9\\-\\.\\_\\~${isIRI ? '\\xA0-\\u200D\\u2010-\\u2029\\u202F-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF' : ''}]`;
          const HEXDIG$$ = '[0-9A-Fa-f]'; // case-insensitive
          const PCT_ENCODED$ = subexp(`${subexp(`%[EFef]${HEXDIG$$}%${HEXDIG$$}${HEXDIG$$}%${HEXDIG$$}${HEXDIG$$}`)}|${subexp(`%[89A-Fa-f]${HEXDIG$$}%${HEXDIG$$}${HEXDIG$$}`)}|${subexp(`%${HEXDIG$$}${HEXDIG$$}`)}`); // expanded
          // RFC 5322, except these symbols as per RFC 6068: @ : / ? # [ ] & ; =
          // const ATEXT$$ = "[A-Za-z0-9\\!\\#\\$\\%\\&\\'\\*\\+\\-\\/\\=\\?\\^\\_\\`\\{\\|\\}\\~]";
          // const WSP$$ = "[\\x20\\x09]";
          // const OBS_QTEXT$$ = "[\\x01-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]";  //(%d1-8 / %d11-12 / %d14-31 / %d127)
          // const QTEXT$$ = merge("[\\x21\\x23-\\x5B\\x5D-\\x7E]", OBS_QTEXT$$);  //%d33 / %d35-91 / %d93-126 / obs-qtext
          // const VCHAR$$ = "[\\x21-\\x7E]";
          // const WSP$$ = "[\\x20\\x09]";
          // const OBS_QP$ = subexp("\\\\" + merge("[\\x00\\x0D\\x0A]", OBS_QTEXT$$));  //%d0 / CR / LF / obs-qtext
          // const FWS$ = subexp(subexp(WSP$$ + "*" + "\\x0D\\x0A") + "?" + WSP$$ + "+");
          // const QUOTED_PAIR$ = subexp(subexp("\\\\" + subexp(VCHAR$$ + "|" + WSP$$)) + "|" + OBS_QP$);
          // const QUOTED_STRING$ = subexp('\\"' + subexp(FWS$ + "?" + QCONTENT$) + "*" + FWS$ + "?" + '\\"');
          const ATEXT$$ = '[A-Za-z0-9\\!\\$\\%\\\'\\*\\+\\-\\^\\_\\`\\{\\|\\}\\~]';
          const QTEXT$$ = '[\\!\\$\\%\\\'\\(\\)\\*\\+\\,\\-\\.0-9\\<\\>A-Z\\x5E-\\x7E]';
          const VCHAR$$ = merge(QTEXT$$, '[\\"\\\\]');
          const SOME_DELIMS$$ = '[\\!\\$\\\'\\(\\)\\*\\+\\,\\;\\:\\@]';
          const UNRESERVED = new RegExp(UNRESERVED$$, 'g');
          const PCT_ENCODED = new RegExp(PCT_ENCODED$, 'g');
          const NOT_LOCAL_PART = new RegExp(merge('[^]', ATEXT$$, '[\\.]', '[\\"]', VCHAR$$), 'g');
          const NOT_HFNAME = new RegExp(merge('[^]', UNRESERVED$$, SOME_DELIMS$$), 'g');
          const NOT_HFVALUE = NOT_HFNAME;
          function decodeUnreserved(str) {
            const decStr = pctDecChars(str);
            return !decStr.match(UNRESERVED) ? str : decStr;
          }
          const handler$4 = {
            scheme: 'mailto',
            parse: function parse$$1(components, options) {
              const mailtoComponents = components;
              const to = mailtoComponents.to = mailtoComponents.path ? mailtoComponents.path.split(',') : [];
              mailtoComponents.path = undefined;
              if (mailtoComponents.query) {
                let unknownHeaders = false;
                const headers = {};
                const hfields = mailtoComponents.query.split('&');
                for (let x = 0, xl = hfields.length; x < xl; ++x) {
                  const hfield = hfields[x].split('=');
                  switch (hfield[0]) {
                    case 'to':
                      var toAddrs = hfield[1].split(',');
                      for (let _x = 0, _xl = toAddrs.length; _x < _xl; ++_x) {
                        to.push(toAddrs[_x]);
                      }
                      break;
                    case 'subject':
                      mailtoComponents.subject = unescapeComponent(hfield[1], options);
                      break;
                    case 'body':
                      mailtoComponents.body = unescapeComponent(hfield[1], options);
                      break;
                    default:
                      unknownHeaders = true;
                      headers[unescapeComponent(hfield[0], options)] = unescapeComponent(hfield[1], options);
                      break;
                  }
                }
                if (unknownHeaders) mailtoComponents.headers = headers;
              }
              mailtoComponents.query = undefined;
              for (let _x2 = 0, _xl2 = to.length; _x2 < _xl2; ++_x2) {
                const addr = to[_x2].split('@');
                addr[0] = unescapeComponent(addr[0]);
                if (!options.unicodeSupport) {
                // convert Unicode IDN -> ASCII IDN
                  try {
                    addr[1] = punycode.toASCII(unescapeComponent(addr[1], options).toLowerCase());
                  } catch (e) {
                    mailtoComponents.error = mailtoComponents.error || `Email address's domain name can not be converted to ASCII via punycode: ${e}`;
                  }
                } else {
                  addr[1] = unescapeComponent(addr[1], options).toLowerCase();
                }
                to[_x2] = addr.join('@');
              }
              return mailtoComponents;
            },
            serialize: function serialize$$1(mailtoComponents, options) {
              const components = mailtoComponents;
              const to = toArray(mailtoComponents.to);
              if (to) {
                for (let x = 0, xl = to.length; x < xl; ++x) {
                  const toAddr = String(to[x]);
                  const atIdx = toAddr.lastIndexOf('@');
                  const localPart = toAddr.slice(0, atIdx).replace(PCT_ENCODED, decodeUnreserved)
                    .replace(PCT_ENCODED, toUpperCase)
                    .replace(NOT_LOCAL_PART, pctEncChar);
                  let domain = toAddr.slice(atIdx + 1);
                  // convert IDN via punycode
                  try {
                    domain = !options.iri ? punycode.toASCII(unescapeComponent(domain, options).toLowerCase()) : punycode.toUnicode(domain);
                  } catch (e) {
                    components.error = components.error || `Email address's domain name can not be converted to ${!options.iri ? 'ASCII' : 'Unicode'} via punycode: ${e}`;
                  }
                  to[x] = `${localPart}@${domain}`;
                }
                components.path = to.join(',');
              }
              const headers = mailtoComponents.headers = mailtoComponents.headers || {};
              if (mailtoComponents.subject) headers.subject = mailtoComponents.subject;
              if (mailtoComponents.body) headers.body = mailtoComponents.body;
              const fields = [];
              for (const name in headers) {
                if (headers[name] !== O[name]) {
                  fields.push(`${name.replace(PCT_ENCODED, decodeUnreserved).replace(PCT_ENCODED, toUpperCase)
                    .replace(NOT_HFNAME, pctEncChar)}=${headers[name].replace(PCT_ENCODED, decodeUnreserved).replace(PCT_ENCODED, toUpperCase)
                    .replace(NOT_HFVALUE, pctEncChar)}`);
                }
              }
              if (fields.length) {
                components.query = fields.join('&');
              }
              return components;
            },
          };

          const URN_PARSE = /^([^\:]+)\:(.*)/;
          // RFC 2141
          const handler$5 = {
            scheme: 'urn',
            parse: function parse$$1(components, options) {
              const matches = components.path && components.path.match(URN_PARSE);
              let urnComponents = components;
              if (matches) {
                const scheme = options.scheme || urnComponents.scheme || 'urn';
                const nid = matches[1].toLowerCase();
                const nss = matches[2];
                const urnScheme = `${scheme}:${options.nid || nid}`;
                const schemeHandler = SCHEMES[urnScheme];
                urnComponents.nid = nid;
                urnComponents.nss = nss;
                urnComponents.path = undefined;
                if (schemeHandler) {
                  urnComponents = schemeHandler.parse(urnComponents, options);
                }
              } else {
                urnComponents.error = urnComponents.error || 'URN can not be parsed.';
              }
              return urnComponents;
            },
            serialize: function serialize$$1(urnComponents, options) {
              const scheme = options.scheme || urnComponents.scheme || 'urn';
              const { nid } = urnComponents;
              const urnScheme = `${scheme}:${options.nid || nid}`;
              const schemeHandler = SCHEMES[urnScheme];
              if (schemeHandler) {
                urnComponents = schemeHandler.serialize(urnComponents, options);
              }
              const uriComponents = urnComponents;
              const { nss } = urnComponents;
              uriComponents.path = `${nid || options.nid}:${nss}`;
              return uriComponents;
            },
          };

          const UUID = /^[0-9A-Fa-f]{8}(?:\-[0-9A-Fa-f]{4}){3}\-[0-9A-Fa-f]{12}$/;
          // RFC 4122
          const handler$6 = {
            scheme: 'urn:uuid',
            parse: function parse(urnComponents, options) {
              const uuidComponents = urnComponents;
              uuidComponents.uuid = uuidComponents.nss;
              uuidComponents.nss = undefined;
              if (!options.tolerant && (!uuidComponents.uuid || !uuidComponents.uuid.match(UUID))) {
                uuidComponents.error = uuidComponents.error || 'UUID is not valid.';
              }
              return uuidComponents;
            },
            serialize: function serialize(uuidComponents, options) {
              const urnComponents = uuidComponents;
              // normalize UUID
              urnComponents.nss = (uuidComponents.uuid || '').toLowerCase();
              return urnComponents;
            },
          };

          SCHEMES[handler.scheme] = handler;
          SCHEMES[handler$1.scheme] = handler$1;
          SCHEMES[handler$2.scheme] = handler$2;
          SCHEMES[handler$3.scheme] = handler$3;
          SCHEMES[handler$4.scheme] = handler$4;
          SCHEMES[handler$5.scheme] = handler$5;
          SCHEMES[handler$6.scheme] = handler$6;

          exports.SCHEMES = SCHEMES;
          exports.pctEncChar = pctEncChar;
          exports.pctDecChars = pctDecChars;
          exports.parse = parse;
          exports.removeDotSegments = removeDotSegments;
          exports.serialize = serialize;
          exports.resolveComponents = resolveComponents;
          exports.resolve = resolve;
          exports.normalize = normalize;
          exports.equal = equal;
          exports.escapeComponent = escapeComponent;
          exports.unescapeComponent = unescapeComponent;

          Object.defineProperty(exports, '__esModule', { value: true });
        })));
        // # sourceMappingURL=uri.all.js.map
        /***/ }),

      /***/ 2834:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        // style-loader: Adds some css to the DOM by adding a <style> tag

        // load the styles
        let content = __webpack_require__(7794);
        if (content.__esModule) content = content.default;
        if (typeof content === 'string') content = [[module.id, content, '']];
        if (content.locals) module.exports = content.locals;
        // add the styles to the DOM
        const add = (__webpack_require__(5346)/* ["default"] */ .Z);
        const update = add('6e2ca1e2', content, true, {});
        /***/ }),

      /***/ 5346:
      /***/ (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
        'use strict';

        // EXPORTS
        __webpack_require__.d(__webpack_exports__, {
          Z() {
            return /* binding */ addStylesClient;
          },
        });

        ;// CONCATENATED MODULE: ./node_modules/vue-style-loader/lib/listToStyles.js
        /**
 * Translates the list format produced by css-loader into something
 * easier to manipulate.
 */
        function listToStyles(parentId, list) {
          const styles = [];
          const newStyles = {};
          for (let i = 0; i < list.length; i++) {
            const item = list[i];
            const id = item[0];
            const css = item[1];
            const media = item[2];
            const sourceMap = item[3];
            const part = {
              id: `${parentId}:${i}`,
              css,
              media,
              sourceMap,
            };
            if (!newStyles[id]) {
              styles.push(newStyles[id] = { id, parts: [part] });
            } else {
              newStyles[id].parts.push(part);
            }
          }
          return styles;
        }

        ;// CONCATENATED MODULE: ./node_modules/vue-style-loader/lib/addStylesClient.js
        /*
  MIT License http://www.opensource.org/licenses/mit-license.php
  Author Tobias Koppers @sokra
  Modified by Evan You @yyx990803
*/


        const hasDocument = typeof document !== 'undefined';

        if (typeof DEBUG !== 'undefined' && DEBUG) {
          if (!hasDocument) {
            throw new Error('vue-style-loader cannot be used in a non-browser environment. '
    + 'Use { target: \'node\' } in your Webpack config to indicate a server-rendering environment.');
          }
        }

        /*
type StyleObject = {
  id: number;
  parts: Array<StyleObjectPart>
}

type StyleObjectPart = {
  css: string;
  media: string;
  sourceMap: ?string
}
*/

        const stylesInDom = {/*
  [id: number]: {
    id: number,
    refs: number,
    parts: Array<(obj?: StyleObjectPart) => void>
  }
*/};

        const head = hasDocument && (document.head || document.getElementsByTagName('head')[0]);
        let singletonElement = null;
        let singletonCounter = 0;
        let isProduction = false;
        const noop = function () {};
        let options = null;
        const ssrIdKey = 'data-vue-ssr-id';

        // Force single-tag solution on IE6-9, which has a hard limit on the # of <style>
        // tags it will allow on a page
        const isOldIE = typeof navigator !== 'undefined' && /msie [6-9]\b/.test(navigator.userAgent.toLowerCase());

        function addStylesClient(parentId, list, _isProduction, _options) {
          isProduction = _isProduction;

          options = _options || {};

          let styles = listToStyles(parentId, list);
          addStylesToDom(styles);

          return function update(newList) {
            const mayRemove = [];
            for (var i = 0; i < styles.length; i++) {
              const item = styles[i];
              var domStyle = stylesInDom[item.id];
              domStyle.refs--;
              mayRemove.push(domStyle);
            }
            if (newList) {
              styles = listToStyles(parentId, newList);
              addStylesToDom(styles);
            } else {
              styles = [];
            }
            for (var i = 0; i < mayRemove.length; i++) {
              var domStyle = mayRemove[i];
              if (domStyle.refs === 0) {
                for (let j = 0; j < domStyle.parts.length; j++) {
                  domStyle.parts[j]();
                }
                delete stylesInDom[domStyle.id];
              }
            }
          };
        }

        function addStylesToDom(styles /* Array<StyleObject> */) {
          for (let i = 0; i < styles.length; i++) {
            const item = styles[i];
            const domStyle = stylesInDom[item.id];
            if (domStyle) {
              domStyle.refs++;
              for (var j = 0; j < domStyle.parts.length; j++) {
                domStyle.parts[j](item.parts[j]);
              }
              for (; j < item.parts.length; j++) {
                domStyle.parts.push(addStyle(item.parts[j]));
              }
              if (domStyle.parts.length > item.parts.length) {
                domStyle.parts.length = item.parts.length;
              }
            } else {
              const parts = [];
              for (var j = 0; j < item.parts.length; j++) {
                parts.push(addStyle(item.parts[j]));
              }
              stylesInDom[item.id] = { id: item.id, refs: 1, parts };
            }
          }
        }

        function createStyleElement() {
          const styleElement = document.createElement('style');
          styleElement.type = 'text/css';
          head.appendChild(styleElement);
          return styleElement;
        }

        function addStyle(obj /* StyleObjectPart */) {
          let update; let remove;
          let styleElement = document.querySelector(`style[${ssrIdKey}~="${obj.id}"]`);

          if (styleElement) {
            if (isProduction) {
              // has SSR styles and in production mode.
              // simply do nothing.
              return noop;
            }
            // has SSR styles but in dev mode.
            // for some reason Chrome can't handle source map in server-rendered
            // style tags - source maps in <style> only works if the style tag is
            // created and inserted dynamically. So we remove the server rendered
            // styles and inject new ones.
            styleElement.parentNode.removeChild(styleElement);
          }

          if (isOldIE) {
            // use singleton mode for IE9.
            const styleIndex = singletonCounter++;
            styleElement = singletonElement || (singletonElement = createStyleElement());
            update = applyToSingletonTag.bind(null, styleElement, styleIndex, false);
            remove = applyToSingletonTag.bind(null, styleElement, styleIndex, true);
          } else {
            // use multi-style-tag mode in all other cases
            styleElement = createStyleElement();
            update = applyToTag.bind(null, styleElement);
            remove = function () {
              styleElement.parentNode.removeChild(styleElement);
            };
          }

          update(obj);

          return function updateStyle(newObj /* StyleObjectPart */) {
            if (newObj) {
              if (newObj.css === obj.css
          && newObj.media === obj.media
          && newObj.sourceMap === obj.sourceMap) {
                return;
              }
              update(obj = newObj);
            } else {
              remove();
            }
          };
        }

        const replaceText = (function () {
          const textStore = [];

          return function (index, replacement) {
            textStore[index] = replacement;
            return textStore.filter(Boolean).join('\n');
          };
        }());

        function applyToSingletonTag(styleElement, index, remove, obj) {
          const css = remove ? '' : obj.css;

          if (styleElement.styleSheet) {
            styleElement.styleSheet.cssText = replaceText(index, css);
          } else {
            const cssNode = document.createTextNode(css);
            const { childNodes } = styleElement;
            if (childNodes[index]) styleElement.removeChild(childNodes[index]);
            if (childNodes.length) {
              styleElement.insertBefore(cssNode, childNodes[index]);
            } else {
              styleElement.appendChild(cssNode);
            }
          }
        }

        function applyToTag(styleElement, obj) {
          let { css } = obj;
          const { media } = obj;
          const { sourceMap } = obj;

          if (media) {
            styleElement.setAttribute('media', media);
          }
          if (options.ssrId) {
            styleElement.setAttribute(ssrIdKey, obj.id);
          }

          if (sourceMap) {
            // https://developer.chrome.com/devtools/docs/javascript-debugging
            // this makes source maps inside style tags work properly in Chrome
            css += `\n/*# sourceURL=${sourceMap.sources[0]} */`;
            // http://stackoverflow.com/a/26603875
            css += `\n/*# sourceMappingURL=data:application/json;base64,${btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap))))} */`;
          }

          if (styleElement.styleSheet) {
            styleElement.styleSheet.cssText = css;
          } else {
            while (styleElement.firstChild) {
              styleElement.removeChild(styleElement.firstChild);
            }
            styleElement.appendChild(document.createTextNode(css));
          }
        }
        /***/ }),

      /***/ 748:
      /***/ (function (module) {
        'use strict';
        module.exports = __WEBPACK_EXTERNAL_MODULE__748__;
        /***/ }),

      /***/ 3897:
      /***/ (function (module) {
        function _arrayLikeToArray(arr, len) {
          if (len == null || len > arr.length) len = arr.length;
          for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i];
          return arr2;
        }
        module.exports = _arrayLikeToArray, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 3405:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        const arrayLikeToArray = __webpack_require__(3897);
        function _arrayWithoutHoles(arr) {
          if (Array.isArray(arr)) return arrayLikeToArray(arr);
        }
        module.exports = _arrayWithoutHoles, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 8416:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        const toPropertyKey = __webpack_require__(4062);
        function _defineProperty(obj, key, value) {
          key = toPropertyKey(key);
          if (key in obj) {
            Object.defineProperty(obj, key, {
              value,
              enumerable: true,
              configurable: true,
              writable: true,
            });
          } else {
            obj[key] = value;
          }
          return obj;
        }
        module.exports = _defineProperty, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 4836:
      /***/ (function (module) {
        function _interopRequireDefault(obj) {
          return obj && obj.__esModule ? obj : {
            default: obj,
          };
        }
        module.exports = _interopRequireDefault, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 9498:
      /***/ (function (module) {
        function _iterableToArray(iter) {
          if (typeof Symbol !== 'undefined' && iter[Symbol.iterator] != null || iter['@@iterator'] != null) return Array.from(iter);
        }
        module.exports = _iterableToArray, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 2281:
      /***/ (function (module) {
        function _nonIterableSpread() {
          throw new TypeError('Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.');
        }
        module.exports = _nonIterableSpread, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 3012:
      /***/ (function (module) {
        function _objectDestructuringEmpty(obj) {
          if (obj == null) throw new TypeError(`Cannot destructure ${obj}`);
        }
        module.exports = _objectDestructuringEmpty, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 215:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        const objectWithoutPropertiesLoose = __webpack_require__(7071);
        function _objectWithoutProperties(source, excluded) {
          if (source == null) return {};
          const target = objectWithoutPropertiesLoose(source, excluded);
          let key; let i;
          if (Object.getOwnPropertySymbols) {
            const sourceSymbolKeys = Object.getOwnPropertySymbols(source);
            for (i = 0; i < sourceSymbolKeys.length; i++) {
              key = sourceSymbolKeys[i];
              if (excluded.indexOf(key) >= 0) continue;
              if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue;
              target[key] = source[key];
            }
          }
          return target;
        }
        module.exports = _objectWithoutProperties, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 7071:
      /***/ (function (module) {
        function _objectWithoutPropertiesLoose(source, excluded) {
          if (source == null) return {};
          const target = {};
          const sourceKeys = Object.keys(source);
          let key; let i;
          for (i = 0; i < sourceKeys.length; i++) {
            key = sourceKeys[i];
            if (excluded.indexOf(key) >= 0) continue;
            target[key] = source[key];
          }
          return target;
        }
        module.exports = _objectWithoutPropertiesLoose, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 861:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        const arrayWithoutHoles = __webpack_require__(3405);
        const iterableToArray = __webpack_require__(9498);
        const unsupportedIterableToArray = __webpack_require__(6116);
        const nonIterableSpread = __webpack_require__(2281);
        function _toConsumableArray(arr) {
          return arrayWithoutHoles(arr) || iterableToArray(arr) || unsupportedIterableToArray(arr) || nonIterableSpread();
        }
        module.exports = _toConsumableArray, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 5036:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        const _typeof = (__webpack_require__(8698).default);
        function _toPrimitive(input, hint) {
          if (_typeof(input) !== 'object' || input === null) return input;
          const prim = input[Symbol.toPrimitive];
          if (prim !== undefined) {
            const res = prim.call(input, hint || 'default');
            if (_typeof(res) !== 'object') return res;
            throw new TypeError('@@toPrimitive must return a primitive value.');
          }
          return (hint === 'string' ? String : Number)(input);
        }
        module.exports = _toPrimitive, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 4062:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        const _typeof = (__webpack_require__(8698).default);
        const toPrimitive = __webpack_require__(5036);
        function _toPropertyKey(arg) {
          const key = toPrimitive(arg, 'string');
          return _typeof(key) === 'symbol' ? key : String(key);
        }
        module.exports = _toPropertyKey, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 8698:
      /***/ (function (module) {
        function _typeof(o) {
          '@babel/helpers - typeof';

          return (module.exports = _typeof = 'function' === typeof Symbol && 'symbol' === typeof Symbol.iterator ? function (o) {
            return typeof o;
          } : function (o) {
            return o && 'function' === typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? 'symbol' : typeof o;
          }, module.exports.__esModule = true, module.exports.default = module.exports), _typeof(o);
        }
        module.exports = _typeof, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 6116:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        const arrayLikeToArray = __webpack_require__(3897);
        function _unsupportedIterableToArray(o, minLen) {
          if (!o) return;
          if (typeof o === 'string') return arrayLikeToArray(o, minLen);
          let n = Object.prototype.toString.call(o).slice(8, -1);
          if (n === 'Object' && o.constructor) n = o.constructor.name;
          if (n === 'Map' || n === 'Set') return Array.from(o);
          if (n === 'Arguments' || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return arrayLikeToArray(o, minLen);
        }
        module.exports = _unsupportedIterableToArray, module.exports.__esModule = true, module.exports.default = module.exports;
        /***/ }),

      /***/ 509:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const isCallable = __webpack_require__(9985);
        const tryToString = __webpack_require__(3691);

        const $TypeError = TypeError;

        // `Assert: IsCallable(argument) is true`
        module.exports = function (argument) {
          if (isCallable(argument)) return argument;
          throw new $TypeError(`${tryToString(argument)} is not a function`);
        };
        /***/ }),

      /***/ 3550:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const isCallable = __webpack_require__(9985);

        const $String = String;
        const $TypeError = TypeError;

        module.exports = function (argument) {
          if (typeof argument === 'object' || isCallable(argument)) return argument;
          throw new $TypeError(`Can't set ${$String(argument)} as a prototype`);
        };
        /***/ }),

      /***/ 7370:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const wellKnownSymbol = __webpack_require__(4201);
        const create = __webpack_require__(5391);
        const defineProperty = (__webpack_require__(2560).f);

        const UNSCOPABLES = wellKnownSymbol('unscopables');
        const ArrayPrototype = Array.prototype;

        // Array.prototype[@@unscopables]
        // https://tc39.es/ecma262/#sec-array.prototype-@@unscopables
        if (ArrayPrototype[UNSCOPABLES] === undefined) {
          defineProperty(ArrayPrototype, UNSCOPABLES, {
            configurable: true,
            value: create(null),
          });
        }

        // add a key to Array.prototype[@@unscopables]
        module.exports = function (key) {
          ArrayPrototype[UNSCOPABLES][key] = true;
        };
        /***/ }),

      /***/ 767:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const isPrototypeOf = __webpack_require__(3622);

        const $TypeError = TypeError;

        module.exports = function (it, Prototype) {
          if (isPrototypeOf(Prototype, it)) return it;
          throw new $TypeError('Incorrect invocation');
        };
        /***/ }),

      /***/ 5027:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const isObject = __webpack_require__(8999);

        const $String = String;
        const $TypeError = TypeError;

        // `Assert: Type(argument) is Object`
        module.exports = function (argument) {
          if (isObject(argument)) return argument;
          throw new $TypeError(`${$String(argument)} is not an object`);
        };
        /***/ }),

      /***/ 1655:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        // FF26- bug: ArrayBuffers are non-extensible, but Object.isExtensible does not report it
        const fails = __webpack_require__(3689);

        module.exports = fails(() => {
          if (typeof ArrayBuffer === 'function') {
            const buffer = new ArrayBuffer(8);
            // eslint-disable-next-line es/no-object-isextensible, es/no-object-defineproperty -- safe
            if (Object.isExtensible(buffer)) Object.defineProperty(buffer, 'a', { value: 8 });
          }
        });
        /***/ }),

      /***/ 2872:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const toObject = __webpack_require__(690);
        const toAbsoluteIndex = __webpack_require__(7578);
        const lengthOfArrayLike = __webpack_require__(6310);

        // `Array.prototype.fill` method implementation
        // https://tc39.es/ecma262/#sec-array.prototype.fill
        module.exports = function fill(value /* , start = 0, end = @length */) {
          const O = toObject(this);
          const length = lengthOfArrayLike(O);
          const argumentsLength = arguments.length;
          let index = toAbsoluteIndex(argumentsLength > 1 ? arguments[1] : undefined, length);
          const end = argumentsLength > 2 ? arguments[2] : undefined;
          const endPos = end === undefined ? length : toAbsoluteIndex(end, length);
          while (endPos > index) O[index++] = value;
          return O;
        };
        /***/ }),

      /***/ 7612:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $forEach = (__webpack_require__(2960).forEach);
        const arrayMethodIsStrict = __webpack_require__(6834);

        const STRICT_METHOD = arrayMethodIsStrict('forEach');

        // `Array.prototype.forEach` method implementation
        // https://tc39.es/ecma262/#sec-array.prototype.foreach
        module.exports = !STRICT_METHOD ? function forEach(callbackfn /* , thisArg */) {
          return $forEach(this, callbackfn, arguments.length > 1 ? arguments[1] : undefined);
          // eslint-disable-next-line es/no-array-prototype-foreach -- safe
        } : [].forEach;
        /***/ }),

      /***/ 4328:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const toIndexedObject = __webpack_require__(5290);
        const toAbsoluteIndex = __webpack_require__(7578);
        const lengthOfArrayLike = __webpack_require__(6310);

        // `Array.prototype.{ indexOf, includes }` methods implementation
        const createMethod = function (IS_INCLUDES) {
          return function ($this, el, fromIndex) {
            const O = toIndexedObject($this);
            const length = lengthOfArrayLike(O);
            let index = toAbsoluteIndex(fromIndex, length);
            let value;
            // Array#includes uses SameValueZero equality algorithm
            // eslint-disable-next-line no-self-compare -- NaN check
            if (IS_INCLUDES && el !== el) while (length > index) {
              value = O[index++];
              // eslint-disable-next-line no-self-compare -- NaN check
              if (value !== value) return true;
              // Array#indexOf ignores holes, Array#includes - not
            } else for (;length > index; index++) {
              if ((IS_INCLUDES || index in O) && O[index] === el) return IS_INCLUDES || index || 0;
            } return !IS_INCLUDES && -1;
          };
        };

        module.exports = {
          // `Array.prototype.includes` method
          // https://tc39.es/ecma262/#sec-array.prototype.includes
          includes: createMethod(true),
          // `Array.prototype.indexOf` method
          // https://tc39.es/ecma262/#sec-array.prototype.indexof
          indexOf: createMethod(false),
        };
        /***/ }),

      /***/ 2960:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const bind = __webpack_require__(4071);
        const uncurryThis = __webpack_require__(8844);
        const IndexedObject = __webpack_require__(4413);
        const toObject = __webpack_require__(690);
        const lengthOfArrayLike = __webpack_require__(6310);
        const arraySpeciesCreate = __webpack_require__(7120);

        const push = uncurryThis([].push);

        // `Array.prototype.{ forEach, map, filter, some, every, find, findIndex, filterReject }` methods implementation
        const createMethod = function (TYPE) {
          const IS_MAP = TYPE === 1;
          const IS_FILTER = TYPE === 2;
          const IS_SOME = TYPE === 3;
          const IS_EVERY = TYPE === 4;
          const IS_FIND_INDEX = TYPE === 6;
          const IS_FILTER_REJECT = TYPE === 7;
          const NO_HOLES = TYPE === 5 || IS_FIND_INDEX;
          return function ($this, callbackfn, that, specificCreate) {
            const O = toObject($this);
            const self = IndexedObject(O);
            const boundFunction = bind(callbackfn, that);
            const length = lengthOfArrayLike(self);
            let index = 0;
            const create = specificCreate || arraySpeciesCreate;
            const target = IS_MAP ? create($this, length) : IS_FILTER || IS_FILTER_REJECT ? create($this, 0) : undefined;
            let value; let result;
            for (;length > index; index++) if (NO_HOLES || index in self) {
              value = self[index];
              result = boundFunction(value, index, O);
              if (TYPE) {
                if (IS_MAP) target[index] = result; // map
                else if (result) switch (TYPE) {
                  case 3: return true;              // some
                  case 5: return value;             // find
                  case 6: return index;             // findIndex
                  case 2: push(target, value);      // filter
                } else switch (TYPE) {
                  case 4: return false;             // every
                  case 7: push(target, value);      // filterReject
                }
              }
            }
            return IS_FIND_INDEX ? -1 : IS_SOME || IS_EVERY ? IS_EVERY : target;
          };
        };

        module.exports = {
          // `Array.prototype.forEach` method
          // https://tc39.es/ecma262/#sec-array.prototype.foreach
          forEach: createMethod(0),
          // `Array.prototype.map` method
          // https://tc39.es/ecma262/#sec-array.prototype.map
          map: createMethod(1),
          // `Array.prototype.filter` method
          // https://tc39.es/ecma262/#sec-array.prototype.filter
          filter: createMethod(2),
          // `Array.prototype.some` method
          // https://tc39.es/ecma262/#sec-array.prototype.some
          some: createMethod(3),
          // `Array.prototype.every` method
          // https://tc39.es/ecma262/#sec-array.prototype.every
          every: createMethod(4),
          // `Array.prototype.find` method
          // https://tc39.es/ecma262/#sec-array.prototype.find
          find: createMethod(5),
          // `Array.prototype.findIndex` method
          // https://tc39.es/ecma262/#sec-array.prototype.findIndex
          findIndex: createMethod(6),
          // `Array.prototype.filterReject` method
          // https://github.com/tc39/proposal-array-filtering
          filterReject: createMethod(7),
        };
        /***/ }),

      /***/ 9042:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const fails = __webpack_require__(3689);
        const wellKnownSymbol = __webpack_require__(4201);
        const V8_VERSION = __webpack_require__(3615);

        const SPECIES = wellKnownSymbol('species');

        module.exports = function (METHOD_NAME) {
          // We can't use this feature detection in V8 since it causes
          // deoptimization and serious performance degradation
          // https://github.com/zloirock/core-js/issues/677
          return V8_VERSION >= 51 || !fails(() => {
            const array = [];
            const constructor = array.constructor = {};
            constructor[SPECIES] = function () {
              return { foo: 1 };
            };
            return array[METHOD_NAME](Boolean).foo !== 1;
          });
        };
        /***/ }),

      /***/ 6834:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const fails = __webpack_require__(3689);

        module.exports = function (METHOD_NAME, argument) {
          const method = [][METHOD_NAME];
          return !!method && fails(() => {
            // eslint-disable-next-line no-useless-call -- required for testing
            method.call(null, argument || (() => 1), 1);
          });
        };
        /***/ }),

      /***/ 5649:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const isArray = __webpack_require__(2297);

        const $TypeError = TypeError;
        // eslint-disable-next-line es/no-object-getownpropertydescriptor -- safe
        const { getOwnPropertyDescriptor } = Object;

        // Safari < 13 does not throw an error in this case
        const SILENT_ON_NON_WRITABLE_LENGTH_SET = DESCRIPTORS && !(function () {
          // makes no sense without proper strict mode support
          if (this !== undefined) return true;
          try {
            // eslint-disable-next-line es/no-object-defineproperty -- safe
            Object.defineProperty([], 'length', { writable: false }).length = 1;
          } catch (error) {
            return error instanceof TypeError;
          }
        }());

        module.exports = SILENT_ON_NON_WRITABLE_LENGTH_SET ? function (O, length) {
          if (isArray(O) && !getOwnPropertyDescriptor(O, 'length').writable) {
            throw new $TypeError('Cannot set read only .length');
          } return O.length = length;
        } : function (O, length) {
          return O.length = length;
        };
        /***/ }),

      /***/ 9015:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const toAbsoluteIndex = __webpack_require__(7578);
        const lengthOfArrayLike = __webpack_require__(6310);
        const createProperty = __webpack_require__(6522);

        const $Array = Array;
        const { max } = Math;

        module.exports = function (O, start, end) {
          const length = lengthOfArrayLike(O);
          let k = toAbsoluteIndex(start, length);
          const fin = toAbsoluteIndex(end === undefined ? length : end, length);
          const result = $Array(max(fin - k, 0));
          let n = 0;
          for (; k < fin; k++, n++) createProperty(result, n, O[k]);
          result.length = n;
          return result;
        };
        /***/ }),

      /***/ 6004:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);

        module.exports = uncurryThis([].slice);
        /***/ }),

      /***/ 5271:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const isArray = __webpack_require__(2297);
        const isConstructor = __webpack_require__(9429);
        const isObject = __webpack_require__(8999);
        const wellKnownSymbol = __webpack_require__(4201);

        const SPECIES = wellKnownSymbol('species');
        const $Array = Array;

        // a part of `ArraySpeciesCreate` abstract operation
        // https://tc39.es/ecma262/#sec-arrayspeciescreate
        module.exports = function (originalArray) {
          let C;
          if (isArray(originalArray)) {
            C = originalArray.constructor;
            // cross-realm fallback
            if (isConstructor(C) && (C === $Array || isArray(C.prototype))) C = undefined;
            else if (isObject(C)) {
              C = C[SPECIES];
              if (C === null) C = undefined;
            }
          } return C === undefined ? $Array : C;
        };
        /***/ }),

      /***/ 7120:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const arraySpeciesConstructor = __webpack_require__(5271);

        // `ArraySpeciesCreate` abstract operation
        // https://tc39.es/ecma262/#sec-arrayspeciescreate
        module.exports = function (originalArray, length) {
          return new (arraySpeciesConstructor(originalArray))(length === 0 ? 0 : length);
        };
        /***/ }),

      /***/ 6431:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const wellKnownSymbol = __webpack_require__(4201);

        const ITERATOR = wellKnownSymbol('iterator');
        let SAFE_CLOSING = false;

        try {
          let called = 0;
          const iteratorWithReturn = {
            next() {
              return { done: !!called++ };
            },
            return() {
              SAFE_CLOSING = true;
            },
          };
          iteratorWithReturn[ITERATOR] = function () {
            return this;
          };
          // eslint-disable-next-line es/no-array-from, no-throw-literal -- required for testing
          Array.from(iteratorWithReturn, () => {
            throw 2;
          });
        } catch (error) { /* empty */ }

        module.exports = function (exec, SKIP_CLOSING) {
          try {
            if (!SKIP_CLOSING && !SAFE_CLOSING) return false;
          } catch (error) {
            return false;
          } // workaround of old WebKit + `eval` bug
          let ITERATION_SUPPORT = false;
          try {
            const object = {};
            object[ITERATOR] = function () {
              return {
                next() {
                  return { done: ITERATION_SUPPORT = true };
                },
              };
            };
            exec(object);
          } catch (error) { /* empty */ }
          return ITERATION_SUPPORT;
        };
        /***/ }),

      /***/ 6648:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);

        const toString = uncurryThis({}.toString);
        const stringSlice = uncurryThis(''.slice);

        module.exports = function (it) {
          return stringSlice(toString(it), 8, -1);
        };
        /***/ }),

      /***/ 926:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const TO_STRING_TAG_SUPPORT = __webpack_require__(3043);
        const isCallable = __webpack_require__(9985);
        const classofRaw = __webpack_require__(6648);
        const wellKnownSymbol = __webpack_require__(4201);

        const TO_STRING_TAG = wellKnownSymbol('toStringTag');
        const $Object = Object;

        // ES3 wrong here
        const CORRECT_ARGUMENTS = classofRaw(function () {
          return arguments;
        }()) === 'Arguments';

        // fallback for IE11 Script Access Denied error
        const tryGet = function (it, key) {
          try {
            return it[key];
          } catch (error) { /* empty */ }
        };

        // getting tag from ES6+ `Object.prototype.toString`
        module.exports = TO_STRING_TAG_SUPPORT ? classofRaw : function (it) {
          let O; let tag; let result;
          return it === undefined ? 'Undefined' : it === null ? 'Null'
          // @@toStringTag case
            : typeof (tag = tryGet(O = $Object(it), TO_STRING_TAG)) === 'string' ? tag
            // builtinTag case
              : CORRECT_ARGUMENTS ? classofRaw(O)
              // ES3 arguments fallback
                : (result = classofRaw(O)) === 'Object' && isCallable(O.callee) ? 'Arguments' : result;
        };
        /***/ }),

      /***/ 637:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const defineBuiltIns = __webpack_require__(6045);
        const { getWeakData } = __webpack_require__(5375);
        const anInstance = __webpack_require__(767);
        const anObject = __webpack_require__(5027);
        const isNullOrUndefined = __webpack_require__(981);
        const isObject = __webpack_require__(8999);
        const iterate = __webpack_require__(8734);
        const ArrayIterationModule = __webpack_require__(2960);
        const hasOwn = __webpack_require__(6812);
        const InternalStateModule = __webpack_require__(618);

        const setInternalState = InternalStateModule.set;
        const internalStateGetterFor = InternalStateModule.getterFor;
        const { find } = ArrayIterationModule;
        const { findIndex } = ArrayIterationModule;
        const splice = uncurryThis([].splice);
        let id = 0;

        // fallback for uncaught frozen keys
        const uncaughtFrozenStore = function (state) {
          return state.frozen || (state.frozen = new UncaughtFrozenStore());
        };

        var UncaughtFrozenStore = function () {
          this.entries = [];
        };

        const findUncaughtFrozen = function (store, key) {
          return find(store.entries, it => it[0] === key);
        };

        UncaughtFrozenStore.prototype = {
          get(key) {
            const entry = findUncaughtFrozen(this, key);
            if (entry) return entry[1];
          },
          has(key) {
            return !!findUncaughtFrozen(this, key);
          },
          set(key, value) {
            const entry = findUncaughtFrozen(this, key);
            if (entry) entry[1] = value;
            else this.entries.push([key, value]);
          },
          delete(key) {
            const index = findIndex(this.entries, it => it[0] === key);
            if (~index) splice(this.entries, index, 1);
            return !!~index;
          },
        };

        module.exports = {
          getConstructor(wrapper, CONSTRUCTOR_NAME, IS_MAP, ADDER) {
            const Constructor = wrapper((that, iterable) => {
              anInstance(that, Prototype);
              setInternalState(that, {
                type: CONSTRUCTOR_NAME,
                id: id++,
                frozen: undefined,
              });
              if (!isNullOrUndefined(iterable)) iterate(iterable, that[ADDER], { that, AS_ENTRIES: IS_MAP });
            });

            var Prototype = Constructor.prototype;

            const getInternalState = internalStateGetterFor(CONSTRUCTOR_NAME);

            const define = function (that, key, value) {
              const state = getInternalState(that);
              const data = getWeakData(anObject(key), true);
              if (data === true) uncaughtFrozenStore(state).set(key, value);
              else data[state.id] = value;
              return that;
            };

            defineBuiltIns(Prototype, {
              // `{ WeakMap, WeakSet }.prototype.delete(key)` methods
              // https://tc39.es/ecma262/#sec-weakmap.prototype.delete
              // https://tc39.es/ecma262/#sec-weakset.prototype.delete
              delete(key) {
                const state = getInternalState(this);
                if (!isObject(key)) return false;
                const data = getWeakData(key);
                if (data === true) return uncaughtFrozenStore(state).delete(key);
                return data && hasOwn(data, state.id) && delete data[state.id];
              },
              // `{ WeakMap, WeakSet }.prototype.has(key)` methods
              // https://tc39.es/ecma262/#sec-weakmap.prototype.has
              // https://tc39.es/ecma262/#sec-weakset.prototype.has
              has: function has(key) {
                const state = getInternalState(this);
                if (!isObject(key)) return false;
                const data = getWeakData(key);
                if (data === true) return uncaughtFrozenStore(state).has(key);
                return data && hasOwn(data, state.id);
              },
            });

            defineBuiltIns(Prototype, IS_MAP ? {
              // `WeakMap.prototype.get(key)` method
              // https://tc39.es/ecma262/#sec-weakmap.prototype.get
              get: function get(key) {
                const state = getInternalState(this);
                if (isObject(key)) {
                  const data = getWeakData(key);
                  if (data === true) return uncaughtFrozenStore(state).get(key);
                  return data ? data[state.id] : undefined;
                }
              },
              // `WeakMap.prototype.set(key, value)` method
              // https://tc39.es/ecma262/#sec-weakmap.prototype.set
              set: function set(key, value) {
                return define(this, key, value);
              },
            } : {
              // `WeakSet.prototype.add(value)` method
              // https://tc39.es/ecma262/#sec-weakset.prototype.add
              add: function add(value) {
                return define(this, value, true);
              },
            });

            return Constructor;
          },
        };
        /***/ }),

      /***/ 319:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const global = __webpack_require__(9037);
        const uncurryThis = __webpack_require__(8844);
        const isForced = __webpack_require__(5266);
        const defineBuiltIn = __webpack_require__(1880);
        const InternalMetadataModule = __webpack_require__(5375);
        const iterate = __webpack_require__(8734);
        const anInstance = __webpack_require__(767);
        const isCallable = __webpack_require__(9985);
        const isNullOrUndefined = __webpack_require__(981);
        const isObject = __webpack_require__(8999);
        const fails = __webpack_require__(3689);
        const checkCorrectnessOfIteration = __webpack_require__(6431);
        const setToStringTag = __webpack_require__(5997);
        const inheritIfRequired = __webpack_require__(3457);

        module.exports = function (CONSTRUCTOR_NAME, wrapper, common) {
          const IS_MAP = CONSTRUCTOR_NAME.indexOf('Map') !== -1;
          const IS_WEAK = CONSTRUCTOR_NAME.indexOf('Weak') !== -1;
          const ADDER = IS_MAP ? 'set' : 'add';
          const NativeConstructor = global[CONSTRUCTOR_NAME];
          const NativePrototype = NativeConstructor && NativeConstructor.prototype;
          let Constructor = NativeConstructor;
          const exported = {};

          const fixMethod = function (KEY) {
            const uncurriedNativeMethod = uncurryThis(NativePrototype[KEY]);
            defineBuiltIn(
              NativePrototype, KEY,
              KEY === 'add' ? function add(value) {
                uncurriedNativeMethod(this, value === 0 ? 0 : value);
                return this;
              } : KEY === 'delete' ? function (key) {
                return IS_WEAK && !isObject(key) ? false : uncurriedNativeMethod(this, key === 0 ? 0 : key);
              } : KEY === 'get' ? function get(key) {
                return IS_WEAK && !isObject(key) ? undefined : uncurriedNativeMethod(this, key === 0 ? 0 : key);
              } : KEY === 'has' ? function has(key) {
                return IS_WEAK && !isObject(key) ? false : uncurriedNativeMethod(this, key === 0 ? 0 : key);
              } : function set(key, value) {
                uncurriedNativeMethod(this, key === 0 ? 0 : key, value);
                return this;
              },
            );
          };

          const REPLACE = isForced(
            CONSTRUCTOR_NAME,
            !isCallable(NativeConstructor) || !(IS_WEAK || NativePrototype.forEach && !fails(() => {
              new NativeConstructor().entries()
                .next();
            })),
          );

          if (REPLACE) {
            // create collection constructor
            Constructor = common.getConstructor(wrapper, CONSTRUCTOR_NAME, IS_MAP, ADDER);
            InternalMetadataModule.enable();
          } else if (isForced(CONSTRUCTOR_NAME, true)) {
            const instance = new Constructor();
            // early implementations not supports chaining
            const HASNT_CHAINING = instance[ADDER](IS_WEAK ? {} : -0, 1) !== instance;
            // V8 ~ Chromium 40- weak-collections throws on primitives, but should return false
            const THROWS_ON_PRIMITIVES = fails(() => {
              instance.has(1);
            });
            // most early implementations doesn't supports iterables, most modern - not close it correctly
            // eslint-disable-next-line no-new -- required for testing
            const ACCEPT_ITERABLES = checkCorrectnessOfIteration((iterable) => {
              new NativeConstructor(iterable);
            });
            // for early implementations -0 and +0 not the same
            const BUGGY_ZERO = !IS_WEAK && fails(() => {
              // V8 ~ Chromium 42- fails only with 5+ elements
              const $instance = new NativeConstructor();
              let index = 5;
              while (index--) $instance[ADDER](index, index);
              return !$instance.has(-0);
            });

            if (!ACCEPT_ITERABLES) {
              Constructor = wrapper((dummy, iterable) => {
                anInstance(dummy, NativePrototype);
                const that = inheritIfRequired(new NativeConstructor(), dummy, Constructor);
                if (!isNullOrUndefined(iterable)) iterate(iterable, that[ADDER], { that, AS_ENTRIES: IS_MAP });
                return that;
              });
              Constructor.prototype = NativePrototype;
              NativePrototype.constructor = Constructor;
            }

            if (THROWS_ON_PRIMITIVES || BUGGY_ZERO) {
              fixMethod('delete');
              fixMethod('has');
              IS_MAP && fixMethod('get');
            }

            if (BUGGY_ZERO || HASNT_CHAINING) fixMethod(ADDER);

            // weak collections should not contains .clear method
            if (IS_WEAK && NativePrototype.clear) delete NativePrototype.clear;
          }

          exported[CONSTRUCTOR_NAME] = Constructor;
          $({ global: true, constructor: true, forced: Constructor !== NativeConstructor }, exported);

          setToStringTag(Constructor, CONSTRUCTOR_NAME);

          if (!IS_WEAK) common.setStrong(Constructor, CONSTRUCTOR_NAME, IS_MAP);

          return Constructor;
        };
        /***/ }),

      /***/ 8758:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const hasOwn = __webpack_require__(6812);
        const ownKeys = __webpack_require__(9152);
        const getOwnPropertyDescriptorModule = __webpack_require__(2474);
        const definePropertyModule = __webpack_require__(2560);

        module.exports = function (target, source, exceptions) {
          const keys = ownKeys(source);
          const defineProperty = definePropertyModule.f;
          const getOwnPropertyDescriptor = getOwnPropertyDescriptorModule.f;
          for (let i = 0; i < keys.length; i++) {
            const key = keys[i];
            if (!hasOwn(target, key) && !(exceptions && hasOwn(exceptions, key))) {
              defineProperty(target, key, getOwnPropertyDescriptor(source, key));
            }
          }
        };
        /***/ }),

      /***/ 1748:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const fails = __webpack_require__(3689);

        module.exports = !fails(() => {
          function F() { /* empty */ }
          F.prototype.constructor = null;
          // eslint-disable-next-line es/no-object-getprototypeof -- required for testing
          return Object.getPrototypeOf(new F()) !== F.prototype;
        });
        /***/ }),

      /***/ 7807:
      /***/ (function (module) {
        'use strict';

        // `CreateIterResultObject` abstract operation
        // https://tc39.es/ecma262/#sec-createiterresultobject
        module.exports = function (value, done) {
          return { value, done };
        };
        /***/ }),

      /***/ 5773:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const definePropertyModule = __webpack_require__(2560);
        const createPropertyDescriptor = __webpack_require__(5684);

        module.exports = DESCRIPTORS ? function (object, key, value) {
          return definePropertyModule.f(object, key, createPropertyDescriptor(1, value));
        } : function (object, key, value) {
          object[key] = value;
          return object;
        };
        /***/ }),

      /***/ 5684:
      /***/ (function (module) {
        'use strict';

        module.exports = function (bitmap, value) {
          return {
            enumerable: !(bitmap & 1),
            configurable: !(bitmap & 2),
            writable: !(bitmap & 4),
            value,
          };
        };
        /***/ }),

      /***/ 6522:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const toPropertyKey = __webpack_require__(8360);
        const definePropertyModule = __webpack_require__(2560);
        const createPropertyDescriptor = __webpack_require__(5684);

        module.exports = function (object, key, value) {
          const propertyKey = toPropertyKey(key);
          if (propertyKey in object) definePropertyModule.f(object, propertyKey, createPropertyDescriptor(0, value));
          else object[propertyKey] = value;
        };
        /***/ }),

      /***/ 2148:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const makeBuiltIn = __webpack_require__(8702);
        const defineProperty = __webpack_require__(2560);

        module.exports = function (target, name, descriptor) {
          if (descriptor.get) makeBuiltIn(descriptor.get, name, { getter: true });
          if (descriptor.set) makeBuiltIn(descriptor.set, name, { setter: true });
          return defineProperty.f(target, name, descriptor);
        };
        /***/ }),

      /***/ 1880:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const isCallable = __webpack_require__(9985);
        const definePropertyModule = __webpack_require__(2560);
        const makeBuiltIn = __webpack_require__(8702);
        const defineGlobalProperty = __webpack_require__(5014);

        module.exports = function (O, key, value, options) {
          if (!options) options = {};
          let simple = options.enumerable;
          const name = options.name !== undefined ? options.name : key;
          if (isCallable(value)) makeBuiltIn(value, name, options);
          if (options.global) {
            if (simple) O[key] = value;
            else defineGlobalProperty(key, value);
          } else {
            try {
              if (!options.unsafe) delete O[key];
              else if (O[key]) simple = true;
            } catch (error) { /* empty */ }
            if (simple) O[key] = value;
            else definePropertyModule.f(O, key, {
              value,
              enumerable: false,
              configurable: !options.nonConfigurable,
              writable: !options.nonWritable,
            });
          } return O;
        };
        /***/ }),

      /***/ 6045:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const defineBuiltIn = __webpack_require__(1880);

        module.exports = function (target, src, options) {
          for (const key in src) defineBuiltIn(target, key, src[key], options);
          return target;
        };
        /***/ }),

      /***/ 5014:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);

        // eslint-disable-next-line es/no-object-defineproperty -- safe
        const { defineProperty } = Object;

        module.exports = function (key, value) {
          try {
            defineProperty(global, key, { value, configurable: true, writable: true });
          } catch (error) {
            global[key] = value;
          } return value;
        };
        /***/ }),

      /***/ 8494:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const tryToString = __webpack_require__(3691);

        const $TypeError = TypeError;

        module.exports = function (O, P) {
          if (!delete O[P]) throw new $TypeError(`Cannot delete property ${tryToString(P)} of ${tryToString(O)}`);
        };
        /***/ }),

      /***/ 7697:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const fails = __webpack_require__(3689);

        // Detect IE8's incomplete defineProperty implementation
        module.exports = !fails(() =>
          // eslint-disable-next-line es/no-object-defineproperty -- required for testing
          Object.defineProperty({}, 1, { get() {
            return 7;
          } })[1] !== 7);
        /***/ }),

      /***/ 2659:
      /***/ (function (module) {
        'use strict';

        const documentAll = typeof document === 'object' && document.all;

        // https://tc39.es/ecma262/#sec-IsHTMLDDA-internal-slot
        // eslint-disable-next-line unicorn/no-typeof-undefined -- required for testing
        const IS_HTMLDDA = typeof documentAll === 'undefined' && documentAll !== undefined;

        module.exports = {
          all: documentAll,
          IS_HTMLDDA,
        };
        /***/ }),

      /***/ 6420:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);
        const isObject = __webpack_require__(8999);

        const { document } = global;
        // typeof document.createElement is 'object' in old IE
        const EXISTS = isObject(document) && isObject(document.createElement);

        module.exports = function (it) {
          return EXISTS ? document.createElement(it) : {};
        };
        /***/ }),

      /***/ 5565:
      /***/ (function (module) {
        'use strict';

        const $TypeError = TypeError;
        const MAX_SAFE_INTEGER = 0x1FFFFFFFFFFFFF; // 2 ** 53 - 1 == 9007199254740991

        module.exports = function (it) {
          if (it > MAX_SAFE_INTEGER) throw $TypeError('Maximum allowed index exceeded');
          return it;
        };
        /***/ }),

      /***/ 6338:
      /***/ (function (module) {
        'use strict';

        // iterable DOM collections
        // flag - `iterable` interface - 'entries', 'keys', 'values', 'forEach' methods
        module.exports = {
          CSSRuleList: 0,
          CSSStyleDeclaration: 0,
          CSSValueList: 0,
          ClientRectList: 0,
          DOMRectList: 0,
          DOMStringList: 0,
          DOMTokenList: 1,
          DataTransferItemList: 0,
          FileList: 0,
          HTMLAllCollection: 0,
          HTMLCollection: 0,
          HTMLFormElement: 0,
          HTMLSelectElement: 0,
          MediaList: 0,
          MimeTypeArray: 0,
          NamedNodeMap: 0,
          NodeList: 1,
          PaintRequestList: 0,
          Plugin: 0,
          PluginArray: 0,
          SVGLengthList: 0,
          SVGNumberList: 0,
          SVGPathSegList: 0,
          SVGPointList: 0,
          SVGStringList: 0,
          SVGTransformList: 0,
          SourceBufferList: 0,
          StyleSheetList: 0,
          TextTrackCueList: 0,
          TextTrackList: 0,
          TouchList: 0,
        };
        /***/ }),

      /***/ 3265:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        // in old WebKit versions, `element.classList` is not an instance of global `DOMTokenList`
        const documentCreateElement = __webpack_require__(6420);

        const { classList } = documentCreateElement('span');
        const DOMTokenListPrototype = classList && classList.constructor && classList.constructor.prototype;

        module.exports = DOMTokenListPrototype === Object.prototype ? undefined : DOMTokenListPrototype;
        /***/ }),

      /***/ 71:
      /***/ (function (module) {
        'use strict';

        module.exports = typeof navigator !== 'undefined' && String(navigator.userAgent) || '';
        /***/ }),

      /***/ 3615:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);
        const userAgent = __webpack_require__(71);

        const { process } = global;
        const { Deno } = global;
        const versions = process && process.versions || Deno && Deno.version;
        const v8 = versions && versions.v8;
        let match; let version;

        if (v8) {
          match = v8.split('.');
          // in old Chrome, versions of V8 isn't V8 = Chrome / 10
          // but their correct versions are not interesting for us
          version = match[0] > 0 && match[0] < 4 ? 1 : +(match[0] + match[1]);
        }

        // BrowserFS NodeJS `process` polyfill incorrectly set `.v8` to `0.0`
        // so check `userAgent` even if `.v8` exists, but 0
        if (!version && userAgent) {
          match = userAgent.match(/Edge\/(\d+)/);
          if (!match || match[1] >= 74) {
            match = userAgent.match(/Chrome\/(\d+)/);
            if (match) version = +match[1];
          }
        }

        module.exports = version;
        /***/ }),

      /***/ 2739:
      /***/ (function (module) {
        'use strict';

        // IE8- don't enum bug keys
        module.exports = [
          'constructor',
          'hasOwnProperty',
          'isPrototypeOf',
          'propertyIsEnumerable',
          'toLocaleString',
          'toString',
          'valueOf',
        ];
        /***/ }),

      /***/ 9989:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);
        const getOwnPropertyDescriptor = (__webpack_require__(2474).f);
        const createNonEnumerableProperty = __webpack_require__(5773);
        const defineBuiltIn = __webpack_require__(1880);
        const defineGlobalProperty = __webpack_require__(5014);
        const copyConstructorProperties = __webpack_require__(8758);
        const isForced = __webpack_require__(5266);

        /*
  options.target         - name of the target object
  options.global         - target is the global object
  options.stat           - export as static methods of target
  options.proto          - export as prototype methods of target
  options.real           - real prototype method for the `pure` version
  options.forced         - export even if the native feature is available
  options.bind           - bind methods to the target, required for the `pure` version
  options.wrap           - wrap constructors to preventing global pollution, required for the `pure` version
  options.unsafe         - use the simple assignment of property instead of delete + defineProperty
  options.sham           - add a flag to not completely full polyfills
  options.enumerable     - export as enumerable property
  options.dontCallGetSet - prevent calling a getter on target
  options.name           - the .name of the function if it does not match the key
*/
        module.exports = function (options, source) {
          const TARGET = options.target;
          const GLOBAL = options.global;
          const STATIC = options.stat;
          let FORCED; let target; let key; let targetProperty; let sourceProperty; let descriptor;
          if (GLOBAL) {
            target = global;
          } else if (STATIC) {
            target = global[TARGET] || defineGlobalProperty(TARGET, {});
          } else {
            target = (global[TARGET] || {}).prototype;
          }
          if (target) for (key in source) {
            sourceProperty = source[key];
            if (options.dontCallGetSet) {
              descriptor = getOwnPropertyDescriptor(target, key);
              targetProperty = descriptor && descriptor.value;
            } else targetProperty = target[key];
            FORCED = isForced(GLOBAL ? key : TARGET + (STATIC ? '.' : '#') + key, options.forced);
            // contained in target
            if (!FORCED && targetProperty !== undefined) {
              if (typeof sourceProperty === typeof targetProperty) continue;
              copyConstructorProperties(sourceProperty, targetProperty);
            }
            // add a flag to not completely full polyfills
            if (options.sham || (targetProperty && targetProperty.sham)) {
              createNonEnumerableProperty(sourceProperty, 'sham', true);
            }
            defineBuiltIn(target, key, sourceProperty, options);
          }
        };
        /***/ }),

      /***/ 3689:
      /***/ (function (module) {
        'use strict';

        module.exports = function (exec) {
          try {
            return !!exec();
          } catch (error) {
            return true;
          }
        };
        /***/ }),

      /***/ 1594:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const fails = __webpack_require__(3689);

        module.exports = !fails(() =>
          // eslint-disable-next-line es/no-object-isextensible, es/no-object-preventextensions -- required for testing
          Object.isExtensible(Object.preventExtensions({})));
        /***/ }),

      /***/ 1735:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const NATIVE_BIND = __webpack_require__(7215);

        const FunctionPrototype = Function.prototype;
        const { apply } = FunctionPrototype;
        const { call } = FunctionPrototype;

        // eslint-disable-next-line es/no-reflect -- safe
        module.exports = typeof Reflect === 'object' && Reflect.apply || (NATIVE_BIND ? call.bind(apply) : function () {
          return call.apply(apply, arguments);
        });
        /***/ }),

      /***/ 4071:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(6576);
        const aCallable = __webpack_require__(509);
        const NATIVE_BIND = __webpack_require__(7215);

        const bind = uncurryThis(uncurryThis.bind);

        // optional / simple context binding
        module.exports = function (fn, that) {
          aCallable(fn);
          return that === undefined ? fn : NATIVE_BIND ? bind(fn, that) : function (/* ...args */) {
            return fn.apply(that, arguments);
          };
        };
        /***/ }),

      /***/ 7215:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const fails = __webpack_require__(3689);

        module.exports = !fails(() => {
          // eslint-disable-next-line es/no-function-prototype-bind -- safe
          const test = (function () { /* empty */ }).bind();
          // eslint-disable-next-line no-prototype-builtins -- safe
          return typeof test !== 'function' || test.hasOwnProperty('prototype');
        });
        /***/ }),

      /***/ 2615:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const NATIVE_BIND = __webpack_require__(7215);

        const { call } = Function.prototype;

        module.exports = NATIVE_BIND ? call.bind(call) : function () {
          return call.apply(call, arguments);
        };
        /***/ }),

      /***/ 1236:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const hasOwn = __webpack_require__(6812);

        const FunctionPrototype = Function.prototype;
        // eslint-disable-next-line es/no-object-getownpropertydescriptor -- safe
        const getDescriptor = DESCRIPTORS && Object.getOwnPropertyDescriptor;

        const EXISTS = hasOwn(FunctionPrototype, 'name');
        // additional protection from minified / mangled / dropped function names
        const PROPER = EXISTS && (function something() { /* empty */ }).name === 'something';
        const CONFIGURABLE = EXISTS && (!DESCRIPTORS || (DESCRIPTORS && getDescriptor(FunctionPrototype, 'name').configurable));

        module.exports = {
          EXISTS,
          PROPER,
          CONFIGURABLE,
        };
        /***/ }),

      /***/ 2743:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const aCallable = __webpack_require__(509);

        module.exports = function (object, key, method) {
          try {
            // eslint-disable-next-line es/no-object-getownpropertydescriptor -- safe
            return uncurryThis(aCallable(Object.getOwnPropertyDescriptor(object, key)[method]));
          } catch (error) { /* empty */ }
        };
        /***/ }),

      /***/ 6576:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const classofRaw = __webpack_require__(6648);
        const uncurryThis = __webpack_require__(8844);

        module.exports = function (fn) {
          // Nashorn bug:
          //   https://github.com/zloirock/core-js/issues/1128
          //   https://github.com/zloirock/core-js/issues/1130
          if (classofRaw(fn) === 'Function') return uncurryThis(fn);
        };
        /***/ }),

      /***/ 8844:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const NATIVE_BIND = __webpack_require__(7215);

        const FunctionPrototype = Function.prototype;
        const { call } = FunctionPrototype;
        const uncurryThisWithBind = NATIVE_BIND && FunctionPrototype.bind.bind(call, call);

        module.exports = NATIVE_BIND ? uncurryThisWithBind : function (fn) {
          return function () {
            return call.apply(fn, arguments);
          };
        };
        /***/ }),

      /***/ 6058:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);
        const isCallable = __webpack_require__(9985);

        const aFunction = function (argument) {
          return isCallable(argument) ? argument : undefined;
        };

        module.exports = function (namespace, method) {
          return arguments.length < 2 ? aFunction(global[namespace]) : global[namespace] && global[namespace][method];
        };
        /***/ }),

      /***/ 1664:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const classof = __webpack_require__(926);
        const getMethod = __webpack_require__(4849);
        const isNullOrUndefined = __webpack_require__(981);
        const Iterators = __webpack_require__(9478);
        const wellKnownSymbol = __webpack_require__(4201);

        const ITERATOR = wellKnownSymbol('iterator');

        module.exports = function (it) {
          if (!isNullOrUndefined(it)) return getMethod(it, ITERATOR)
    || getMethod(it, '@@iterator')
    || Iterators[classof(it)];
        };
        /***/ }),

      /***/ 5185:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const call = __webpack_require__(2615);
        const aCallable = __webpack_require__(509);
        const anObject = __webpack_require__(5027);
        const tryToString = __webpack_require__(3691);
        const getIteratorMethod = __webpack_require__(1664);

        const $TypeError = TypeError;

        module.exports = function (argument, usingIterator) {
          const iteratorMethod = arguments.length < 2 ? getIteratorMethod(argument) : usingIterator;
          if (aCallable(iteratorMethod)) return anObject(call(iteratorMethod, argument));
          throw new $TypeError(`${tryToString(argument)} is not iterable`);
        };
        /***/ }),

      /***/ 2643:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const isArray = __webpack_require__(2297);
        const isCallable = __webpack_require__(9985);
        const classof = __webpack_require__(6648);
        const toString = __webpack_require__(4327);

        const push = uncurryThis([].push);

        module.exports = function (replacer) {
          if (isCallable(replacer)) return replacer;
          if (!isArray(replacer)) return;
          const rawLength = replacer.length;
          const keys = [];
          for (let i = 0; i < rawLength; i++) {
            const element = replacer[i];
            if (typeof element === 'string') push(keys, element);
            else if (typeof element === 'number' || classof(element) === 'Number' || classof(element) === 'String') push(keys, toString(element));
          }
          const keysLength = keys.length;
          let root = true;
          return function (key, value) {
            if (root) {
              root = false;
              return value;
            }
            if (isArray(this)) return value;
            for (let j = 0; j < keysLength; j++) if (keys[j] === key) return value;
          };
        };
        /***/ }),

      /***/ 4849:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const aCallable = __webpack_require__(509);
        const isNullOrUndefined = __webpack_require__(981);

        // `GetMethod` abstract operation
        // https://tc39.es/ecma262/#sec-getmethod
        module.exports = function (V, P) {
          const func = V[P];
          return isNullOrUndefined(func) ? undefined : aCallable(func);
        };
        /***/ }),

      /***/ 9037:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const check = function (it) {
          return it && it.Math === Math && it;
        };

        // https://github.com/zloirock/core-js/issues/86#issuecomment-115759028
        module.exports =
  // eslint-disable-next-line es/no-global-this -- safe
  check(typeof globalThis === 'object' && globalThis)
  || check(typeof window === 'object' && window)
  // eslint-disable-next-line no-restricted-globals -- safe
  || check(typeof self === 'object' && self)
  || check(typeof __webpack_require__.g === 'object' && __webpack_require__.g)
  || check(typeof this === 'object' && this)
  // eslint-disable-next-line no-new-func -- fallback
  || (function () {
    return this;
  }()) || Function('return this')();
        /***/ }),

      /***/ 6812:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const toObject = __webpack_require__(690);

        const hasOwnProperty = uncurryThis({}.hasOwnProperty);

        // `HasOwnProperty` abstract operation
        // https://tc39.es/ecma262/#sec-hasownproperty
        // eslint-disable-next-line es/no-object-hasown -- safe
        module.exports = Object.hasOwn || function hasOwn(it, key) {
          return hasOwnProperty(toObject(it), key);
        };
        /***/ }),

      /***/ 7248:
      /***/ (function (module) {
        'use strict';

        module.exports = {};
        /***/ }),

      /***/ 2688:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const getBuiltIn = __webpack_require__(6058);

        module.exports = getBuiltIn('document', 'documentElement');
        /***/ }),

      /***/ 8506:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const fails = __webpack_require__(3689);
        const createElement = __webpack_require__(6420);

        // Thanks to IE8 for its funny defineProperty
        module.exports = !DESCRIPTORS && !fails(() =>
          // eslint-disable-next-line es/no-object-defineproperty -- required for testing
          Object.defineProperty(createElement('div'), 'a', {
            get() {
              return 7;
            },
          }).a !== 7);
        /***/ }),

      /***/ 4413:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const fails = __webpack_require__(3689);
        const classof = __webpack_require__(6648);

        const $Object = Object;
        const split = uncurryThis(''.split);

        // fallback for non-array-like ES3 and non-enumerable old V8 strings
        module.exports = fails(() =>
          // throws an error in rhino, see https://github.com/mozilla/rhino/issues/346
          // eslint-disable-next-line no-prototype-builtins -- safe
          !$Object('z').propertyIsEnumerable(0)) ? function (it) {
            return classof(it) === 'String' ? split(it, '') : $Object(it);
          } : $Object;
        /***/ }),

      /***/ 3457:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const isCallable = __webpack_require__(9985);
        const isObject = __webpack_require__(8999);
        const setPrototypeOf = __webpack_require__(9385);

        // makes subclassing work correct for wrapped built-ins
        module.exports = function ($this, dummy, Wrapper) {
          let NewTarget; let NewTargetPrototype;
          if (
          // it can work only with native `setPrototypeOf`
            setPrototypeOf
    // we haven't completely correct pre-ES6 way for getting `new.target`, so use this
    && isCallable(NewTarget = dummy.constructor)
    && NewTarget !== Wrapper
    && isObject(NewTargetPrototype = NewTarget.prototype)
    && NewTargetPrototype !== Wrapper.prototype
          ) setPrototypeOf($this, NewTargetPrototype);
          return $this;
        };
        /***/ }),

      /***/ 6738:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const isCallable = __webpack_require__(9985);
        const store = __webpack_require__(4091);

        const functionToString = uncurryThis(Function.toString);

        // this helper broken in `core-js@3.4.1-3.4.4`, so we can't use `shared` helper
        if (!isCallable(store.inspectSource)) {
          store.inspectSource = function (it) {
            return functionToString(it);
          };
        }

        module.exports = store.inspectSource;
        /***/ }),

      /***/ 5375:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const uncurryThis = __webpack_require__(8844);
        const hiddenKeys = __webpack_require__(7248);
        const isObject = __webpack_require__(8999);
        const hasOwn = __webpack_require__(6812);
        const defineProperty = (__webpack_require__(2560).f);
        const getOwnPropertyNamesModule = __webpack_require__(2741);
        const getOwnPropertyNamesExternalModule = __webpack_require__(6062);
        const isExtensible = __webpack_require__(7049);
        const uid = __webpack_require__(4630);
        const FREEZING = __webpack_require__(1594);

        let REQUIRED = false;
        const METADATA = uid('meta');
        let id = 0;

        const setMetadata = function (it) {
          defineProperty(it, METADATA, { value: {
            objectID: `O${id++}`, // object ID
            weakData: {},          // weak collections IDs
          } });
        };

        const fastKey = function (it, create) {
          // return a primitive with prefix
          if (!isObject(it)) return typeof it === 'symbol' ? it : (typeof it === 'string' ? 'S' : 'P') + it;
          if (!hasOwn(it, METADATA)) {
            // can't set metadata to uncaught frozen object
            if (!isExtensible(it)) return 'F';
            // not necessary to add metadata
            if (!create) return 'E';
            // add missing metadata
            setMetadata(it);
            // return object ID
          } return it[METADATA].objectID;
        };

        const getWeakData = function (it, create) {
          if (!hasOwn(it, METADATA)) {
            // can't set metadata to uncaught frozen object
            if (!isExtensible(it)) return true;
            // not necessary to add metadata
            if (!create) return false;
            // add missing metadata
            setMetadata(it);
            // return the store of weak collections IDs
          } return it[METADATA].weakData;
        };

        // add metadata on freeze-family methods calling
        const onFreeze = function (it) {
          if (FREEZING && REQUIRED && isExtensible(it) && !hasOwn(it, METADATA)) setMetadata(it);
          return it;
        };

        const enable = function () {
          meta.enable = function () { /* empty */ };
          REQUIRED = true;
          const getOwnPropertyNames = getOwnPropertyNamesModule.f;
          const splice = uncurryThis([].splice);
          const test = {};
          test[METADATA] = 1;

          // prevent exposing of metadata key
          if (getOwnPropertyNames(test).length) {
            getOwnPropertyNamesModule.f = function (it) {
              const result = getOwnPropertyNames(it);
              for (let i = 0, { length } = result; i < length; i++) {
                if (result[i] === METADATA) {
                  splice(result, i, 1);
                  break;
                }
              } return result;
            };

            $({ target: 'Object', stat: true, forced: true }, {
              getOwnPropertyNames: getOwnPropertyNamesExternalModule.f,
            });
          }
        };

        var meta = module.exports = {
          enable,
          fastKey,
          getWeakData,
          onFreeze,
        };

        hiddenKeys[METADATA] = true;
        /***/ }),

      /***/ 618:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const NATIVE_WEAK_MAP = __webpack_require__(9834);
        const global = __webpack_require__(9037);
        const isObject = __webpack_require__(8999);
        const createNonEnumerableProperty = __webpack_require__(5773);
        const hasOwn = __webpack_require__(6812);
        const shared = __webpack_require__(4091);
        const sharedKey = __webpack_require__(2713);
        const hiddenKeys = __webpack_require__(7248);

        const OBJECT_ALREADY_INITIALIZED = 'Object already initialized';
        const { TypeError } = global;
        const { WeakMap } = global;
        let set; let get; let has;

        const enforce = function (it) {
          return has(it) ? get(it) : set(it, {});
        };

        const getterFor = function (TYPE) {
          return function (it) {
            let state;
            if (!isObject(it) || (state = get(it)).type !== TYPE) {
              throw new TypeError(`Incompatible receiver, ${TYPE} required`);
            } return state;
          };
        };

        if (NATIVE_WEAK_MAP || shared.state) {
          const store = shared.state || (shared.state = new WeakMap());
          /* eslint-disable no-self-assign -- prototype methods protection */
          store.get = store.get;
          store.has = store.has;
          store.set = store.set;
          /* eslint-enable no-self-assign -- prototype methods protection */
          set = function (it, metadata) {
            if (store.has(it)) throw new TypeError(OBJECT_ALREADY_INITIALIZED);
            metadata.facade = it;
            store.set(it, metadata);
            return metadata;
          };
          get = function (it) {
            return store.get(it) || {};
          };
          has = function (it) {
            return store.has(it);
          };
        } else {
          const STATE = sharedKey('state');
          hiddenKeys[STATE] = true;
          set = function (it, metadata) {
            if (hasOwn(it, STATE)) throw new TypeError(OBJECT_ALREADY_INITIALIZED);
            metadata.facade = it;
            createNonEnumerableProperty(it, STATE, metadata);
            return metadata;
          };
          get = function (it) {
            return hasOwn(it, STATE) ? it[STATE] : {};
          };
          has = function (it) {
            return hasOwn(it, STATE);
          };
        }

        module.exports = {
          set,
          get,
          has,
          enforce,
          getterFor,
        };
        /***/ }),

      /***/ 3292:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const wellKnownSymbol = __webpack_require__(4201);
        const Iterators = __webpack_require__(9478);

        const ITERATOR = wellKnownSymbol('iterator');
        const ArrayPrototype = Array.prototype;

        // check on default Array iterator
        module.exports = function (it) {
          return it !== undefined && (Iterators.Array === it || ArrayPrototype[ITERATOR] === it);
        };
        /***/ }),

      /***/ 2297:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const classof = __webpack_require__(6648);

        // `IsArray` abstract operation
        // https://tc39.es/ecma262/#sec-isarray
        // eslint-disable-next-line es/no-array-isarray -- safe
        module.exports = Array.isArray || function isArray(argument) {
          return classof(argument) === 'Array';
        };
        /***/ }),

      /***/ 9985:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $documentAll = __webpack_require__(2659);

        const documentAll = $documentAll.all;

        // `IsCallable` abstract operation
        // https://tc39.es/ecma262/#sec-iscallable
        module.exports = $documentAll.IS_HTMLDDA ? function (argument) {
          return typeof argument === 'function' || argument === documentAll;
        } : function (argument) {
          return typeof argument === 'function';
        };
        /***/ }),

      /***/ 9429:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const fails = __webpack_require__(3689);
        const isCallable = __webpack_require__(9985);
        const classof = __webpack_require__(926);
        const getBuiltIn = __webpack_require__(6058);
        const inspectSource = __webpack_require__(6738);

        const noop = function () { /* empty */ };
        const empty = [];
        const construct = getBuiltIn('Reflect', 'construct');
        const constructorRegExp = /^\s*(?:class|function)\b/;
        const exec = uncurryThis(constructorRegExp.exec);
        const INCORRECT_TO_STRING = !constructorRegExp.test(noop);

        const isConstructorModern = function isConstructor(argument) {
          if (!isCallable(argument)) return false;
          try {
            construct(noop, empty, argument);
            return true;
          } catch (error) {
            return false;
          }
        };

        const isConstructorLegacy = function isConstructor(argument) {
          if (!isCallable(argument)) return false;
          switch (classof(argument)) {
            case 'AsyncFunction':
            case 'GeneratorFunction':
            case 'AsyncGeneratorFunction': return false;
          }
          try {
            // we can't check .prototype since constructors produced by .bind haven't it
            // `Function#toString` throws on some built-it function in some legacy engines
            // (for example, `DOMQuad` and similar in FF41-)
            return INCORRECT_TO_STRING || !!exec(constructorRegExp, inspectSource(argument));
          } catch (error) {
            return true;
          }
        };

        isConstructorLegacy.sham = true;

        // `IsConstructor` abstract operation
        // https://tc39.es/ecma262/#sec-isconstructor
        module.exports = !construct || fails(() => {
          let called;
          return isConstructorModern(isConstructorModern.call)
    || !isConstructorModern(Object)
    || !isConstructorModern(() => {
      called = true;
    })
    || called;
        }) ? isConstructorLegacy : isConstructorModern;
        /***/ }),

      /***/ 5266:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const fails = __webpack_require__(3689);
        const isCallable = __webpack_require__(9985);

        const replacement = /#|\.prototype\./;

        const isForced = function (feature, detection) {
          const value = data[normalize(feature)];
          return value === POLYFILL ? true
            : value === NATIVE ? false
              : isCallable(detection) ? fails(detection)
                : !!detection;
        };

        var normalize = isForced.normalize = function (string) {
          return String(string).replace(replacement, '.')
            .toLowerCase();
        };

        var data = isForced.data = {};
        var NATIVE = isForced.NATIVE = 'N';
        var POLYFILL = isForced.POLYFILL = 'P';

        module.exports = isForced;
        /***/ }),

      /***/ 981:
      /***/ (function (module) {
        'use strict';

        // we can't use just `it == null` since of `document.all` special case
        // https://tc39.es/ecma262/#sec-IsHTMLDDA-internal-slot-aec
        module.exports = function (it) {
          return it === null || it === undefined;
        };
        /***/ }),

      /***/ 8999:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const isCallable = __webpack_require__(9985);
        const $documentAll = __webpack_require__(2659);

        const documentAll = $documentAll.all;

        module.exports = $documentAll.IS_HTMLDDA ? function (it) {
          return typeof it === 'object' ? it !== null : isCallable(it) || it === documentAll;
        } : function (it) {
          return typeof it === 'object' ? it !== null : isCallable(it);
        };
        /***/ }),

      /***/ 3931:
      /***/ (function (module) {
        'use strict';

        module.exports = false;
        /***/ }),

      /***/ 734:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const getBuiltIn = __webpack_require__(6058);
        const isCallable = __webpack_require__(9985);
        const isPrototypeOf = __webpack_require__(3622);
        const USE_SYMBOL_AS_UID = __webpack_require__(9525);

        const $Object = Object;

        module.exports = USE_SYMBOL_AS_UID ? function (it) {
          return typeof it === 'symbol';
        } : function (it) {
          const $Symbol = getBuiltIn('Symbol');
          return isCallable($Symbol) && isPrototypeOf($Symbol.prototype, $Object(it));
        };
        /***/ }),

      /***/ 8734:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const bind = __webpack_require__(4071);
        const call = __webpack_require__(2615);
        const anObject = __webpack_require__(5027);
        const tryToString = __webpack_require__(3691);
        const isArrayIteratorMethod = __webpack_require__(3292);
        const lengthOfArrayLike = __webpack_require__(6310);
        const isPrototypeOf = __webpack_require__(3622);
        const getIterator = __webpack_require__(5185);
        const getIteratorMethod = __webpack_require__(1664);
        const iteratorClose = __webpack_require__(2125);

        const $TypeError = TypeError;

        const Result = function (stopped, result) {
          this.stopped = stopped;
          this.result = result;
        };

        const ResultPrototype = Result.prototype;

        module.exports = function (iterable, unboundFunction, options) {
          const that = options && options.that;
          const AS_ENTRIES = !!(options && options.AS_ENTRIES);
          const IS_RECORD = !!(options && options.IS_RECORD);
          const IS_ITERATOR = !!(options && options.IS_ITERATOR);
          const INTERRUPTED = !!(options && options.INTERRUPTED);
          const fn = bind(unboundFunction, that);
          let iterator; let iterFn; let index; let length; let result; let next; let step;

          const stop = function (condition) {
            if (iterator) iteratorClose(iterator, 'normal', condition);
            return new Result(true, condition);
          };

          const callFn = function (value) {
            if (AS_ENTRIES) {
              anObject(value);
              return INTERRUPTED ? fn(value[0], value[1], stop) : fn(value[0], value[1]);
            } return INTERRUPTED ? fn(value, stop) : fn(value);
          };

          if (IS_RECORD) {
            iterator = iterable.iterator;
          } else if (IS_ITERATOR) {
            iterator = iterable;
          } else {
            iterFn = getIteratorMethod(iterable);
            if (!iterFn) throw new $TypeError(`${tryToString(iterable)} is not iterable`);
            // optimisation for array iterators
            if (isArrayIteratorMethod(iterFn)) {
              for (index = 0, length = lengthOfArrayLike(iterable); length > index; index++) {
                result = callFn(iterable[index]);
                if (result && isPrototypeOf(ResultPrototype, result)) return result;
              } return new Result(false);
            }
            iterator = getIterator(iterable, iterFn);
          }

          next = IS_RECORD ? iterable.next : iterator.next;
          while (!(step = call(next, iterator)).done) {
            try {
              result = callFn(step.value);
            } catch (error) {
              iteratorClose(iterator, 'throw', error);
            }
            if (typeof result === 'object' && result && isPrototypeOf(ResultPrototype, result)) return result;
          } return new Result(false);
        };
        /***/ }),

      /***/ 2125:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const call = __webpack_require__(2615);
        const anObject = __webpack_require__(5027);
        const getMethod = __webpack_require__(4849);

        module.exports = function (iterator, kind, value) {
          let innerResult; let innerError;
          anObject(iterator);
          try {
            innerResult = getMethod(iterator, 'return');
            if (!innerResult) {
              if (kind === 'throw') throw value;
              return value;
            }
            innerResult = call(innerResult, iterator);
          } catch (error) {
            innerError = true;
            innerResult = error;
          }
          if (kind === 'throw') throw value;
          if (innerError) throw innerResult;
          anObject(innerResult);
          return value;
        };
        /***/ }),

      /***/ 974:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const { IteratorPrototype } = __webpack_require__(2013);
        const create = __webpack_require__(5391);
        const createPropertyDescriptor = __webpack_require__(5684);
        const setToStringTag = __webpack_require__(5997);
        const Iterators = __webpack_require__(9478);

        const returnThis = function () {
          return this;
        };

        module.exports = function (IteratorConstructor, NAME, next, ENUMERABLE_NEXT) {
          const TO_STRING_TAG = `${NAME} Iterator`;
          IteratorConstructor.prototype = create(IteratorPrototype, { next: createPropertyDescriptor(+!ENUMERABLE_NEXT, next) });
          setToStringTag(IteratorConstructor, TO_STRING_TAG, false, true);
          Iterators[TO_STRING_TAG] = returnThis;
          return IteratorConstructor;
        };
        /***/ }),

      /***/ 1934:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const call = __webpack_require__(2615);
        const IS_PURE = __webpack_require__(3931);
        const FunctionName = __webpack_require__(1236);
        const isCallable = __webpack_require__(9985);
        const createIteratorConstructor = __webpack_require__(974);
        const getPrototypeOf = __webpack_require__(1868);
        const setPrototypeOf = __webpack_require__(9385);
        const setToStringTag = __webpack_require__(5997);
        const createNonEnumerableProperty = __webpack_require__(5773);
        const defineBuiltIn = __webpack_require__(1880);
        const wellKnownSymbol = __webpack_require__(4201);
        const Iterators = __webpack_require__(9478);
        const IteratorsCore = __webpack_require__(2013);

        const PROPER_FUNCTION_NAME = FunctionName.PROPER;
        const CONFIGURABLE_FUNCTION_NAME = FunctionName.CONFIGURABLE;
        const { IteratorPrototype } = IteratorsCore;
        const { BUGGY_SAFARI_ITERATORS } = IteratorsCore;
        const ITERATOR = wellKnownSymbol('iterator');
        const KEYS = 'keys';
        const VALUES = 'values';
        const ENTRIES = 'entries';

        const returnThis = function () {
          return this;
        };

        module.exports = function (Iterable, NAME, IteratorConstructor, next, DEFAULT, IS_SET, FORCED) {
          createIteratorConstructor(IteratorConstructor, NAME, next);

          const getIterationMethod = function (KIND) {
            if (KIND === DEFAULT && defaultIterator) return defaultIterator;
            if (!BUGGY_SAFARI_ITERATORS && KIND && KIND in IterablePrototype) return IterablePrototype[KIND];

            switch (KIND) {
              case KEYS: return function keys() {
                return new IteratorConstructor(this, KIND);
              };
              case VALUES: return function values() {
                return new IteratorConstructor(this, KIND);
              };
              case ENTRIES: return function entries() {
                return new IteratorConstructor(this, KIND);
              };
            }

            return function () {
              return new IteratorConstructor(this);
            };
          };

          const TO_STRING_TAG = `${NAME} Iterator`;
          let INCORRECT_VALUES_NAME = false;
          var IterablePrototype = Iterable.prototype;
          const nativeIterator = IterablePrototype[ITERATOR]
    || IterablePrototype['@@iterator']
    || DEFAULT && IterablePrototype[DEFAULT];
          var defaultIterator = !BUGGY_SAFARI_ITERATORS && nativeIterator || getIterationMethod(DEFAULT);
          const anyNativeIterator = NAME === 'Array' ? IterablePrototype.entries || nativeIterator : nativeIterator;
          let CurrentIteratorPrototype; let methods; let KEY;

          // fix native
          if (anyNativeIterator) {
            CurrentIteratorPrototype = getPrototypeOf(anyNativeIterator.call(new Iterable()));
            if (CurrentIteratorPrototype !== Object.prototype && CurrentIteratorPrototype.next) {
              if (!IS_PURE && getPrototypeOf(CurrentIteratorPrototype) !== IteratorPrototype) {
                if (setPrototypeOf) {
                  setPrototypeOf(CurrentIteratorPrototype, IteratorPrototype);
                } else if (!isCallable(CurrentIteratorPrototype[ITERATOR])) {
                  defineBuiltIn(CurrentIteratorPrototype, ITERATOR, returnThis);
                }
              }
              // Set @@toStringTag to native iterators
              setToStringTag(CurrentIteratorPrototype, TO_STRING_TAG, true, true);
              if (IS_PURE) Iterators[TO_STRING_TAG] = returnThis;
            }
          }

          // fix Array.prototype.{ values, @@iterator }.name in V8 / FF
          if (PROPER_FUNCTION_NAME && DEFAULT === VALUES && nativeIterator && nativeIterator.name !== VALUES) {
            if (!IS_PURE && CONFIGURABLE_FUNCTION_NAME) {
              createNonEnumerableProperty(IterablePrototype, 'name', VALUES);
            } else {
              INCORRECT_VALUES_NAME = true;
              defaultIterator = function values() {
                return call(nativeIterator, this);
              };
            }
          }

          // export additional methods
          if (DEFAULT) {
            methods = {
              values: getIterationMethod(VALUES),
              keys: IS_SET ? defaultIterator : getIterationMethod(KEYS),
              entries: getIterationMethod(ENTRIES),
            };
            if (FORCED) for (KEY in methods) {
              if (BUGGY_SAFARI_ITERATORS || INCORRECT_VALUES_NAME || !(KEY in IterablePrototype)) {
                defineBuiltIn(IterablePrototype, KEY, methods[KEY]);
              }
            } else $({ target: NAME, proto: true, forced: BUGGY_SAFARI_ITERATORS || INCORRECT_VALUES_NAME }, methods);
          }

          // define iterator
          if ((!IS_PURE || FORCED) && IterablePrototype[ITERATOR] !== defaultIterator) {
            defineBuiltIn(IterablePrototype, ITERATOR, defaultIterator, { name: DEFAULT });
          }
          Iterators[NAME] = defaultIterator;

          return methods;
        };
        /***/ }),

      /***/ 2013:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const fails = __webpack_require__(3689);
        const isCallable = __webpack_require__(9985);
        const isObject = __webpack_require__(8999);
        const create = __webpack_require__(5391);
        const getPrototypeOf = __webpack_require__(1868);
        const defineBuiltIn = __webpack_require__(1880);
        const wellKnownSymbol = __webpack_require__(4201);
        const IS_PURE = __webpack_require__(3931);

        const ITERATOR = wellKnownSymbol('iterator');
        let BUGGY_SAFARI_ITERATORS = false;

        // `%IteratorPrototype%` object
        // https://tc39.es/ecma262/#sec-%iteratorprototype%-object
        let IteratorPrototype; let PrototypeOfArrayIteratorPrototype; let arrayIterator;

        /* eslint-disable es/no-array-prototype-keys -- safe */
        if ([].keys) {
          arrayIterator = [].keys();
          // Safari 8 has buggy iterators w/o `next`
          if (!('next' in arrayIterator)) BUGGY_SAFARI_ITERATORS = true;
          else {
            PrototypeOfArrayIteratorPrototype = getPrototypeOf(getPrototypeOf(arrayIterator));
            if (PrototypeOfArrayIteratorPrototype !== Object.prototype) IteratorPrototype = PrototypeOfArrayIteratorPrototype;
          }
        }

        const NEW_ITERATOR_PROTOTYPE = !isObject(IteratorPrototype) || fails(() => {
          const test = {};
          // FF44- legacy iterators case
          return IteratorPrototype[ITERATOR].call(test) !== test;
        });

        if (NEW_ITERATOR_PROTOTYPE) IteratorPrototype = {};
        else if (IS_PURE) IteratorPrototype = create(IteratorPrototype);

        // `%IteratorPrototype%[@@iterator]()` method
        // https://tc39.es/ecma262/#sec-%iteratorprototype%-@@iterator
        if (!isCallable(IteratorPrototype[ITERATOR])) {
          defineBuiltIn(IteratorPrototype, ITERATOR, function () {
            return this;
          });
        }

        module.exports = {
          IteratorPrototype,
          BUGGY_SAFARI_ITERATORS,
        };
        /***/ }),

      /***/ 9478:
      /***/ (function (module) {
        'use strict';

        module.exports = {};
        /***/ }),

      /***/ 6310:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const toLength = __webpack_require__(3126);

        // `LengthOfArrayLike` abstract operation
        // https://tc39.es/ecma262/#sec-lengthofarraylike
        module.exports = function (obj) {
          return toLength(obj.length);
        };
        /***/ }),

      /***/ 8702:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const fails = __webpack_require__(3689);
        const isCallable = __webpack_require__(9985);
        const hasOwn = __webpack_require__(6812);
        const DESCRIPTORS = __webpack_require__(7697);
        const CONFIGURABLE_FUNCTION_NAME = (__webpack_require__(1236).CONFIGURABLE);
        const inspectSource = __webpack_require__(6738);
        const InternalStateModule = __webpack_require__(618);

        const enforceInternalState = InternalStateModule.enforce;
        const getInternalState = InternalStateModule.get;
        const $String = String;
        // eslint-disable-next-line es/no-object-defineproperty -- safe
        const { defineProperty } = Object;
        const stringSlice = uncurryThis(''.slice);
        const replace = uncurryThis(''.replace);
        const join = uncurryThis([].join);

        const CONFIGURABLE_LENGTH = DESCRIPTORS && !fails(() => defineProperty(() => { /* empty */ }, 'length', { value: 8 }).length !== 8);

        const TEMPLATE = String(String).split('String');

        const makeBuiltIn = module.exports = function (value, name, options) {
          if (stringSlice($String(name), 0, 7) === 'Symbol(') {
            name = `[${replace($String(name), /^Symbol\(([^)]*)\)/, '$1')}]`;
          }
          if (options && options.getter) name = `get ${name}`;
          if (options && options.setter) name = `set ${name}`;
          if (!hasOwn(value, 'name') || (CONFIGURABLE_FUNCTION_NAME && value.name !== name)) {
            if (DESCRIPTORS) defineProperty(value, 'name', { value: name, configurable: true });
            else value.name = name;
          }
          if (CONFIGURABLE_LENGTH && options && hasOwn(options, 'arity') && value.length !== options.arity) {
            defineProperty(value, 'length', { value: options.arity });
          }
          try {
            if (options && hasOwn(options, 'constructor') && options.constructor) {
              if (DESCRIPTORS) defineProperty(value, 'prototype', { writable: false });
              // in V8 ~ Chrome 53, prototypes of some methods, like `Array.prototype.values`, are non-writable
            } else if (value.prototype) value.prototype = undefined;
          } catch (error) { /* empty */ }
          const state = enforceInternalState(value);
          if (!hasOwn(state, 'source')) {
            state.source = join(TEMPLATE, typeof name === 'string' ? name : '');
          } return value;
        };

        // add fake Function#toString for correct work wrapped methods / constructors with methods like LoDash isNative
        // eslint-disable-next-line no-extend-native -- required
        Function.prototype.toString = makeBuiltIn(function toString() {
          return isCallable(this) && getInternalState(this).source || inspectSource(this);
        }, 'toString');
        /***/ }),

      /***/ 8828:
      /***/ (function (module) {
        'use strict';

        const { ceil } = Math;
        const { floor } = Math;

        // `Math.trunc` method
        // https://tc39.es/ecma262/#sec-math.trunc
        // eslint-disable-next-line es/no-math-trunc -- safe
        module.exports = Math.trunc || function trunc(x) {
          const n = +x;
          return (n > 0 ? floor : ceil)(n);
        };
        /***/ }),

      /***/ 5394:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const uncurryThis = __webpack_require__(8844);
        const call = __webpack_require__(2615);
        const fails = __webpack_require__(3689);
        const objectKeys = __webpack_require__(300);
        const getOwnPropertySymbolsModule = __webpack_require__(7518);
        const propertyIsEnumerableModule = __webpack_require__(9556);
        const toObject = __webpack_require__(690);
        const IndexedObject = __webpack_require__(4413);

        // eslint-disable-next-line es/no-object-assign -- safe
        const $assign = Object.assign;
        // eslint-disable-next-line es/no-object-defineproperty -- required for testing
        const { defineProperty } = Object;
        const concat = uncurryThis([].concat);

        // `Object.assign` method
        // https://tc39.es/ecma262/#sec-object.assign
        module.exports = !$assign || fails(() => {
          // should have correct order of operations (Edge bug)
          if (DESCRIPTORS && $assign({ b: 1 }, $assign(defineProperty({}, 'a', {
            enumerable: true,
            get() {
              defineProperty(this, 'b', {
                value: 3,
                enumerable: false,
              });
            },
          }), { b: 2 })).b !== 1) return true;
          // should work with symbols and should have deterministic property order (V8 bug)
          const A = {};
          const B = {};
          // eslint-disable-next-line es/no-symbol -- safe
          const symbol = Symbol('assign detection');
          const alphabet = 'abcdefghijklmnopqrst';
          A[symbol] = 7;
          alphabet.split('').forEach((chr) => {
            B[chr] = chr;
          });
          return $assign({}, A)[symbol] !== 7 || objectKeys($assign({}, B)).join('') !== alphabet;
        }) ? function assign(target, source) { // eslint-disable-line no-unused-vars -- required for `.length`
            const T = toObject(target);
            const argumentsLength = arguments.length;
            let index = 1;
            const getOwnPropertySymbols = getOwnPropertySymbolsModule.f;
            const propertyIsEnumerable = propertyIsEnumerableModule.f;
            while (argumentsLength > index) {
              const S = IndexedObject(arguments[index++]);
              const keys = getOwnPropertySymbols ? concat(objectKeys(S), getOwnPropertySymbols(S)) : objectKeys(S);
              const { length } = keys;
              let j = 0;
              var key;
              while (length > j) {
                key = keys[j++];
                if (!DESCRIPTORS || call(propertyIsEnumerable, S, key)) T[key] = S[key];
              }
            } return T;
          } : $assign;
        /***/ }),

      /***/ 5391:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        /* global ActiveXObject -- old IE, WSH */
        const anObject = __webpack_require__(5027);
        const definePropertiesModule = __webpack_require__(8920);
        const enumBugKeys = __webpack_require__(2739);
        const hiddenKeys = __webpack_require__(7248);
        const html = __webpack_require__(2688);
        const documentCreateElement = __webpack_require__(6420);
        const sharedKey = __webpack_require__(2713);

        const GT = '>';
        const LT = '<';
        const PROTOTYPE = 'prototype';
        const SCRIPT = 'script';
        const IE_PROTO = sharedKey('IE_PROTO');

        const EmptyConstructor = function () { /* empty */ };

        const scriptTag = function (content) {
          return `${LT + SCRIPT + GT + content + LT}/${SCRIPT}${GT}`;
        };

        // Create object with fake `null` prototype: use ActiveX Object with cleared prototype
        const NullProtoObjectViaActiveX = function (activeXDocument) {
          activeXDocument.write(scriptTag(''));
          activeXDocument.close();
          const temp = activeXDocument.parentWindow.Object;
          activeXDocument = null; // avoid memory leak
          return temp;
        };

        // Create object with fake `null` prototype: use iframe Object with cleared prototype
        const NullProtoObjectViaIFrame = function () {
          // Thrash, waste and sodomy: IE GC bug
          const iframe = documentCreateElement('iframe');
          const JS = `java${SCRIPT}:`;
          let iframeDocument;
          iframe.style.display = 'none';
          html.appendChild(iframe);
          // https://github.com/zloirock/core-js/issues/475
          iframe.src = String(JS);
          iframeDocument = iframe.contentWindow.document;
          iframeDocument.open();
          iframeDocument.write(scriptTag('document.F=Object'));
          iframeDocument.close();
          return iframeDocument.F;
        };

        // Check for document.domain and active x support
        // No need to use active x approach when document.domain is not set
        // see https://github.com/es-shims/es5-shim/issues/150
        // variation of https://github.com/kitcambridge/es5-shim/commit/4f738ac066346
        // avoid IE GC bug
        let activeXDocument;
        var NullProtoObject = function () {
          try {
            activeXDocument = new ActiveXObject('htmlfile');
          } catch (error) { /* ignore */ }
          NullProtoObject = typeof document !== 'undefined'
            ? document.domain && activeXDocument
              ? NullProtoObjectViaActiveX(activeXDocument) // old IE
              : NullProtoObjectViaIFrame()
            : NullProtoObjectViaActiveX(activeXDocument); // WSH
          let { length } = enumBugKeys;
          while (length--) delete NullProtoObject[PROTOTYPE][enumBugKeys[length]];
          return NullProtoObject();
        };

        hiddenKeys[IE_PROTO] = true;

        // `Object.create` method
        // https://tc39.es/ecma262/#sec-object.create
        // eslint-disable-next-line es/no-object-create -- safe
        module.exports = Object.create || function create(O, Properties) {
          let result;
          if (O !== null) {
            EmptyConstructor[PROTOTYPE] = anObject(O);
            result = new EmptyConstructor();
            EmptyConstructor[PROTOTYPE] = null;
            // add "__proto__" for Object.getPrototypeOf polyfill
            result[IE_PROTO] = O;
          } else result = NullProtoObject();
          return Properties === undefined ? result : definePropertiesModule.f(result, Properties);
        };
        /***/ }),

      /***/ 8920:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const V8_PROTOTYPE_DEFINE_BUG = __webpack_require__(5648);
        const definePropertyModule = __webpack_require__(2560);
        const anObject = __webpack_require__(5027);
        const toIndexedObject = __webpack_require__(5290);
        const objectKeys = __webpack_require__(300);

        // `Object.defineProperties` method
        // https://tc39.es/ecma262/#sec-object.defineproperties
        // eslint-disable-next-line es/no-object-defineproperties -- safe
        exports.f = DESCRIPTORS && !V8_PROTOTYPE_DEFINE_BUG ? Object.defineProperties : function defineProperties(O, Properties) {
          anObject(O);
          const props = toIndexedObject(Properties);
          const keys = objectKeys(Properties);
          const { length } = keys;
          let index = 0;
          let key;
          while (length > index) definePropertyModule.f(O, key = keys[index++], props[key]);
          return O;
        };
        /***/ }),

      /***/ 2560:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const IE8_DOM_DEFINE = __webpack_require__(8506);
        const V8_PROTOTYPE_DEFINE_BUG = __webpack_require__(5648);
        const anObject = __webpack_require__(5027);
        const toPropertyKey = __webpack_require__(8360);

        const $TypeError = TypeError;
        // eslint-disable-next-line es/no-object-defineproperty -- safe
        const $defineProperty = Object.defineProperty;
        // eslint-disable-next-line es/no-object-getownpropertydescriptor -- safe
        const $getOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
        const ENUMERABLE = 'enumerable';
        const CONFIGURABLE = 'configurable';
        const WRITABLE = 'writable';

        // `Object.defineProperty` method
        // https://tc39.es/ecma262/#sec-object.defineproperty
        exports.f = DESCRIPTORS ? V8_PROTOTYPE_DEFINE_BUG ? function defineProperty(O, P, Attributes) {
          anObject(O);
          P = toPropertyKey(P);
          anObject(Attributes);
          if (typeof O === 'function' && P === 'prototype' && 'value' in Attributes && WRITABLE in Attributes && !Attributes[WRITABLE]) {
            const current = $getOwnPropertyDescriptor(O, P);
            if (current && current[WRITABLE]) {
              O[P] = Attributes.value;
              Attributes = {
                configurable: CONFIGURABLE in Attributes ? Attributes[CONFIGURABLE] : current[CONFIGURABLE],
                enumerable: ENUMERABLE in Attributes ? Attributes[ENUMERABLE] : current[ENUMERABLE],
                writable: false,
              };
            }
          } return $defineProperty(O, P, Attributes);
        } : $defineProperty : function defineProperty(O, P, Attributes) {
          anObject(O);
          P = toPropertyKey(P);
          anObject(Attributes);
          if (IE8_DOM_DEFINE) try {
            return $defineProperty(O, P, Attributes);
          } catch (error) { /* empty */ }
          if ('get' in Attributes || 'set' in Attributes) throw new $TypeError('Accessors not supported');
          if ('value' in Attributes) O[P] = Attributes.value;
          return O;
        };
        /***/ }),

      /***/ 2474:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const call = __webpack_require__(2615);
        const propertyIsEnumerableModule = __webpack_require__(9556);
        const createPropertyDescriptor = __webpack_require__(5684);
        const toIndexedObject = __webpack_require__(5290);
        const toPropertyKey = __webpack_require__(8360);
        const hasOwn = __webpack_require__(6812);
        const IE8_DOM_DEFINE = __webpack_require__(8506);

        // eslint-disable-next-line es/no-object-getownpropertydescriptor -- safe
        const $getOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;

        // `Object.getOwnPropertyDescriptor` method
        // https://tc39.es/ecma262/#sec-object.getownpropertydescriptor
        exports.f = DESCRIPTORS ? $getOwnPropertyDescriptor : function getOwnPropertyDescriptor(O, P) {
          O = toIndexedObject(O);
          P = toPropertyKey(P);
          if (IE8_DOM_DEFINE) try {
            return $getOwnPropertyDescriptor(O, P);
          } catch (error) { /* empty */ }
          if (hasOwn(O, P)) return createPropertyDescriptor(!call(propertyIsEnumerableModule.f, O, P), O[P]);
        };
        /***/ }),

      /***/ 6062:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        /* eslint-disable es/no-object-getownpropertynames -- safe */
        const classof = __webpack_require__(6648);
        const toIndexedObject = __webpack_require__(5290);
        const $getOwnPropertyNames = (__webpack_require__(2741).f);
        const arraySlice = __webpack_require__(9015);

        const windowNames = typeof window === 'object' && window && Object.getOwnPropertyNames
          ? Object.getOwnPropertyNames(window) : [];

        const getWindowNames = function (it) {
          try {
            return $getOwnPropertyNames(it);
          } catch (error) {
            return arraySlice(windowNames);
          }
        };

        // fallback for IE11 buggy Object.getOwnPropertyNames with iframe and window
        module.exports.f = function getOwnPropertyNames(it) {
          return windowNames && classof(it) === 'Window'
            ? getWindowNames(it)
            : $getOwnPropertyNames(toIndexedObject(it));
        };
        /***/ }),

      /***/ 2741:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        const internalObjectKeys = __webpack_require__(4948);
        const enumBugKeys = __webpack_require__(2739);

        const hiddenKeys = enumBugKeys.concat('length', 'prototype');

        // `Object.getOwnPropertyNames` method
        // https://tc39.es/ecma262/#sec-object.getownpropertynames
        // eslint-disable-next-line es/no-object-getownpropertynames -- safe
        exports.f = Object.getOwnPropertyNames || function getOwnPropertyNames(O) {
          return internalObjectKeys(O, hiddenKeys);
        };
        /***/ }),

      /***/ 7518:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        // eslint-disable-next-line es/no-object-getownpropertysymbols -- safe
        exports.f = Object.getOwnPropertySymbols;
        /***/ }),

      /***/ 1868:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const hasOwn = __webpack_require__(6812);
        const isCallable = __webpack_require__(9985);
        const toObject = __webpack_require__(690);
        const sharedKey = __webpack_require__(2713);
        const CORRECT_PROTOTYPE_GETTER = __webpack_require__(1748);

        const IE_PROTO = sharedKey('IE_PROTO');
        const $Object = Object;
        const ObjectPrototype = $Object.prototype;

        // `Object.getPrototypeOf` method
        // https://tc39.es/ecma262/#sec-object.getprototypeof
        // eslint-disable-next-line es/no-object-getprototypeof -- safe
        module.exports = CORRECT_PROTOTYPE_GETTER ? $Object.getPrototypeOf : function (O) {
          const object = toObject(O);
          if (hasOwn(object, IE_PROTO)) return object[IE_PROTO];
          const { constructor } = object;
          if (isCallable(constructor) && object instanceof constructor) {
            return constructor.prototype;
          } return object instanceof $Object ? ObjectPrototype : null;
        };
        /***/ }),

      /***/ 7049:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const fails = __webpack_require__(3689);
        const isObject = __webpack_require__(8999);
        const classof = __webpack_require__(6648);
        const ARRAY_BUFFER_NON_EXTENSIBLE = __webpack_require__(1655);

        // eslint-disable-next-line es/no-object-isextensible -- safe
        const $isExtensible = Object.isExtensible;
        const FAILS_ON_PRIMITIVES = fails(() => {
          $isExtensible(1);
        });

        // `Object.isExtensible` method
        // https://tc39.es/ecma262/#sec-object.isextensible
        module.exports = (FAILS_ON_PRIMITIVES || ARRAY_BUFFER_NON_EXTENSIBLE) ? function isExtensible(it) {
          if (!isObject(it)) return false;
          if (ARRAY_BUFFER_NON_EXTENSIBLE && classof(it) === 'ArrayBuffer') return false;
          return $isExtensible ? $isExtensible(it) : true;
        } : $isExtensible;
        /***/ }),

      /***/ 3622:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);

        module.exports = uncurryThis({}.isPrototypeOf);
        /***/ }),

      /***/ 4948:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const hasOwn = __webpack_require__(6812);
        const toIndexedObject = __webpack_require__(5290);
        const { indexOf } = __webpack_require__(4328);
        const hiddenKeys = __webpack_require__(7248);

        const push = uncurryThis([].push);

        module.exports = function (object, names) {
          const O = toIndexedObject(object);
          let i = 0;
          const result = [];
          let key;
          for (key in O) !hasOwn(hiddenKeys, key) && hasOwn(O, key) && push(result, key);
          // Don't enum bug & hidden keys
          while (names.length > i) if (hasOwn(O, key = names[i++])) {
            ~indexOf(result, key) || push(result, key);
          }
          return result;
        };
        /***/ }),

      /***/ 300:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const internalObjectKeys = __webpack_require__(4948);
        const enumBugKeys = __webpack_require__(2739);

        // `Object.keys` method
        // https://tc39.es/ecma262/#sec-object.keys
        // eslint-disable-next-line es/no-object-keys -- safe
        module.exports = Object.keys || function keys(O) {
          return internalObjectKeys(O, enumBugKeys);
        };
        /***/ }),

      /***/ 9556:
      /***/ (function (__unused_webpack_module, exports) {
        'use strict';

        const $propertyIsEnumerable = {}.propertyIsEnumerable;
        // eslint-disable-next-line es/no-object-getownpropertydescriptor -- safe
        const { getOwnPropertyDescriptor } = Object;

        // Nashorn ~ JDK8 bug
        const NASHORN_BUG = getOwnPropertyDescriptor && !$propertyIsEnumerable.call({ 1: 2 }, 1);

        // `Object.prototype.propertyIsEnumerable` method implementation
        // https://tc39.es/ecma262/#sec-object.prototype.propertyisenumerable
        exports.f = NASHORN_BUG ? function propertyIsEnumerable(V) {
          const descriptor = getOwnPropertyDescriptor(this, V);
          return !!descriptor && descriptor.enumerable;
        } : $propertyIsEnumerable;
        /***/ }),

      /***/ 9385:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        /* eslint-disable no-proto -- safe */
        const uncurryThisAccessor = __webpack_require__(2743);
        const anObject = __webpack_require__(5027);
        const aPossiblePrototype = __webpack_require__(3550);

        // `Object.setPrototypeOf` method
        // https://tc39.es/ecma262/#sec-object.setprototypeof
        // Works with __proto__ only. Old v8 can't work with null proto objects.
        // eslint-disable-next-line es/no-object-setprototypeof -- safe
        module.exports = Object.setPrototypeOf || ('__proto__' in {} ? (function () {
          let CORRECT_SETTER = false;
          const test = {};
          let setter;
          try {
            setter = uncurryThisAccessor(Object.prototype, '__proto__', 'set');
            setter(test, []);
            CORRECT_SETTER = test instanceof Array;
          } catch (error) { /* empty */ }
          return function setPrototypeOf(O, proto) {
            anObject(O);
            aPossiblePrototype(proto);
            if (CORRECT_SETTER) setter(O, proto);
            else O.__proto__ = proto;
            return O;
          };
        }()) : undefined);
        /***/ }),

      /***/ 5073:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const TO_STRING_TAG_SUPPORT = __webpack_require__(3043);
        const classof = __webpack_require__(926);

        // `Object.prototype.toString` method implementation
        // https://tc39.es/ecma262/#sec-object.prototype.tostring
        module.exports = TO_STRING_TAG_SUPPORT ? {}.toString : function toString() {
          return `[object ${classof(this)}]`;
        };
        /***/ }),

      /***/ 5899:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const call = __webpack_require__(2615);
        const isCallable = __webpack_require__(9985);
        const isObject = __webpack_require__(8999);

        const $TypeError = TypeError;

        // `OrdinaryToPrimitive` abstract operation
        // https://tc39.es/ecma262/#sec-ordinarytoprimitive
        module.exports = function (input, pref) {
          let fn; let val;
          if (pref === 'string' && isCallable(fn = input.toString) && !isObject(val = call(fn, input))) return val;
          if (isCallable(fn = input.valueOf) && !isObject(val = call(fn, input))) return val;
          if (pref !== 'string' && isCallable(fn = input.toString) && !isObject(val = call(fn, input))) return val;
          throw new $TypeError('Can\'t convert object to primitive value');
        };
        /***/ }),

      /***/ 9152:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const getBuiltIn = __webpack_require__(6058);
        const uncurryThis = __webpack_require__(8844);
        const getOwnPropertyNamesModule = __webpack_require__(2741);
        const getOwnPropertySymbolsModule = __webpack_require__(7518);
        const anObject = __webpack_require__(5027);

        const concat = uncurryThis([].concat);

        // all object keys, includes non-enumerable and symbols
        module.exports = getBuiltIn('Reflect', 'ownKeys') || function ownKeys(it) {
          const keys = getOwnPropertyNamesModule.f(anObject(it));
          const getOwnPropertySymbols = getOwnPropertySymbolsModule.f;
          return getOwnPropertySymbols ? concat(keys, getOwnPropertySymbols(it)) : keys;
        };
        /***/ }),

      /***/ 496:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);

        module.exports = global;
        /***/ }),

      /***/ 4684:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const isNullOrUndefined = __webpack_require__(981);

        const $TypeError = TypeError;

        // `RequireObjectCoercible` abstract operation
        // https://tc39.es/ecma262/#sec-requireobjectcoercible
        module.exports = function (it) {
          if (isNullOrUndefined(it)) throw new $TypeError(`Can't call method on ${it}`);
          return it;
        };
        /***/ }),

      /***/ 5997:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const defineProperty = (__webpack_require__(2560).f);
        const hasOwn = __webpack_require__(6812);
        const wellKnownSymbol = __webpack_require__(4201);

        const TO_STRING_TAG = wellKnownSymbol('toStringTag');

        module.exports = function (target, TAG, STATIC) {
          if (target && !STATIC) target = target.prototype;
          if (target && !hasOwn(target, TO_STRING_TAG)) {
            defineProperty(target, TO_STRING_TAG, { configurable: true, value: TAG });
          }
        };
        /***/ }),

      /***/ 2713:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const shared = __webpack_require__(3430);
        const uid = __webpack_require__(4630);

        const keys = shared('keys');

        module.exports = function (key) {
          return keys[key] || (keys[key] = uid(key));
        };
        /***/ }),

      /***/ 4091:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);
        const defineGlobalProperty = __webpack_require__(5014);

        const SHARED = '__core-js_shared__';
        const store = global[SHARED] || defineGlobalProperty(SHARED, {});

        module.exports = store;
        /***/ }),

      /***/ 3430:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const IS_PURE = __webpack_require__(3931);
        const store = __webpack_require__(4091);

        (module.exports = function (key, value) {
          return store[key] || (store[key] = value !== undefined ? value : {});
        })('versions', []).push({
          version: '3.33.3',
          mode: IS_PURE ? 'pure' : 'global',
          copyright: '© 2014-2023 Denis Pushkarev (zloirock.ru)',
          license: 'https://github.com/zloirock/core-js/blob/v3.33.3/LICENSE',
          source: 'https://github.com/zloirock/core-js',
        });
        /***/ }),

      /***/ 730:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);
        const toIntegerOrInfinity = __webpack_require__(8700);
        const toString = __webpack_require__(4327);
        const requireObjectCoercible = __webpack_require__(4684);

        const charAt = uncurryThis(''.charAt);
        const charCodeAt = uncurryThis(''.charCodeAt);
        const stringSlice = uncurryThis(''.slice);

        const createMethod = function (CONVERT_TO_STRING) {
          return function ($this, pos) {
            const S = toString(requireObjectCoercible($this));
            const position = toIntegerOrInfinity(pos);
            const size = S.length;
            let first; let second;
            if (position < 0 || position >= size) return CONVERT_TO_STRING ? '' : undefined;
            first = charCodeAt(S, position);
            return first < 0xD800 || first > 0xDBFF || position + 1 === size
      || (second = charCodeAt(S, position + 1)) < 0xDC00 || second > 0xDFFF
              ? CONVERT_TO_STRING
                ? charAt(S, position)
                : first
              : CONVERT_TO_STRING
                ? stringSlice(S, position, position + 2)
                : (first - 0xD800 << 10) + (second - 0xDC00) + 0x10000;
          };
        };

        module.exports = {
          // `String.prototype.codePointAt` method
          // https://tc39.es/ecma262/#sec-string.prototype.codepointat
          codeAt: createMethod(false),
          // `String.prototype.at` method
          // https://github.com/mathiasbynens/String.prototype.at
          charAt: createMethod(true),
        };
        /***/ }),

      /***/ 146:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        /* eslint-disable es/no-symbol -- required for testing */
        const V8_VERSION = __webpack_require__(3615);
        const fails = __webpack_require__(3689);
        const global = __webpack_require__(9037);

        const $String = global.String;

        // eslint-disable-next-line es/no-object-getownpropertysymbols -- required for testing
        module.exports = !!Object.getOwnPropertySymbols && !fails(() => {
          const symbol = Symbol('symbol detection');
          // Chrome 38 Symbol has incorrect toString conversion
          // `get-own-property-symbols` polyfill symbols converted to object are not Symbol instances
          // nb: Do not call `String` directly to avoid this being optimized out to `symbol+''` which will,
          // of course, fail.
          return !$String(symbol) || !(Object(symbol) instanceof Symbol)
    // Chrome 38-40 symbols are not inherited from DOM collections prototypes to instances
    || !Symbol.sham && V8_VERSION && V8_VERSION < 41;
        });
        /***/ }),

      /***/ 3032:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const call = __webpack_require__(2615);
        const getBuiltIn = __webpack_require__(6058);
        const wellKnownSymbol = __webpack_require__(4201);
        const defineBuiltIn = __webpack_require__(1880);

        module.exports = function () {
          const Symbol = getBuiltIn('Symbol');
          const SymbolPrototype = Symbol && Symbol.prototype;
          const valueOf = SymbolPrototype && SymbolPrototype.valueOf;
          const TO_PRIMITIVE = wellKnownSymbol('toPrimitive');

          if (SymbolPrototype && !SymbolPrototype[TO_PRIMITIVE]) {
            // `Symbol.prototype[@@toPrimitive]` method
            // https://tc39.es/ecma262/#sec-symbol.prototype-@@toprimitive
            // eslint-disable-next-line no-unused-vars -- required for .length
            defineBuiltIn(SymbolPrototype, TO_PRIMITIVE, function (hint) {
              return call(valueOf, this);
            }, { arity: 1 });
          }
        };
        /***/ }),

      /***/ 6549:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const NATIVE_SYMBOL = __webpack_require__(146);

        /* eslint-disable es/no-symbol -- safe */
        module.exports = NATIVE_SYMBOL && !!Symbol.for && !!Symbol.keyFor;
        /***/ }),

      /***/ 7578:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const toIntegerOrInfinity = __webpack_require__(8700);

        const { max } = Math;
        const { min } = Math;

        // Helper for a popular repeating case of the spec:
        // Let integer be ? ToInteger(index).
        // If integer < 0, let result be max((length + integer), 0); else let result be min(integer, length).
        module.exports = function (index, length) {
          const integer = toIntegerOrInfinity(index);
          return integer < 0 ? max(integer + length, 0) : min(integer, length);
        };
        /***/ }),

      /***/ 5290:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        // toObject with fallback for non-array-like ES3 strings
        const IndexedObject = __webpack_require__(4413);
        const requireObjectCoercible = __webpack_require__(4684);

        module.exports = function (it) {
          return IndexedObject(requireObjectCoercible(it));
        };
        /***/ }),

      /***/ 8700:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const trunc = __webpack_require__(8828);

        // `ToIntegerOrInfinity` abstract operation
        // https://tc39.es/ecma262/#sec-tointegerorinfinity
        module.exports = function (argument) {
          const number = +argument;
          // eslint-disable-next-line no-self-compare -- NaN check
          return number !== number || number === 0 ? 0 : trunc(number);
        };
        /***/ }),

      /***/ 3126:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const toIntegerOrInfinity = __webpack_require__(8700);

        const { min } = Math;

        // `ToLength` abstract operation
        // https://tc39.es/ecma262/#sec-tolength
        module.exports = function (argument) {
          return argument > 0 ? min(toIntegerOrInfinity(argument), 0x1FFFFFFFFFFFFF) : 0; // 2 ** 53 - 1 == 9007199254740991
        };
        /***/ }),

      /***/ 690:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const requireObjectCoercible = __webpack_require__(4684);

        const $Object = Object;

        // `ToObject` abstract operation
        // https://tc39.es/ecma262/#sec-toobject
        module.exports = function (argument) {
          return $Object(requireObjectCoercible(argument));
        };
        /***/ }),

      /***/ 8732:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const call = __webpack_require__(2615);
        const isObject = __webpack_require__(8999);
        const isSymbol = __webpack_require__(734);
        const getMethod = __webpack_require__(4849);
        const ordinaryToPrimitive = __webpack_require__(5899);
        const wellKnownSymbol = __webpack_require__(4201);

        const $TypeError = TypeError;
        const TO_PRIMITIVE = wellKnownSymbol('toPrimitive');

        // `ToPrimitive` abstract operation
        // https://tc39.es/ecma262/#sec-toprimitive
        module.exports = function (input, pref) {
          if (!isObject(input) || isSymbol(input)) return input;
          const exoticToPrim = getMethod(input, TO_PRIMITIVE);
          let result;
          if (exoticToPrim) {
            if (pref === undefined) pref = 'default';
            result = call(exoticToPrim, input, pref);
            if (!isObject(result) || isSymbol(result)) return result;
            throw new $TypeError('Can\'t convert object to primitive value');
          }
          if (pref === undefined) pref = 'number';
          return ordinaryToPrimitive(input, pref);
        };
        /***/ }),

      /***/ 8360:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const toPrimitive = __webpack_require__(8732);
        const isSymbol = __webpack_require__(734);

        // `ToPropertyKey` abstract operation
        // https://tc39.es/ecma262/#sec-topropertykey
        module.exports = function (argument) {
          const key = toPrimitive(argument, 'string');
          return isSymbol(key) ? key : `${key}`;
        };
        /***/ }),

      /***/ 3043:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const wellKnownSymbol = __webpack_require__(4201);

        const TO_STRING_TAG = wellKnownSymbol('toStringTag');
        const test = {};

        test[TO_STRING_TAG] = 'z';

        module.exports = String(test) === '[object z]';
        /***/ }),

      /***/ 4327:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const classof = __webpack_require__(926);

        const $String = String;

        module.exports = function (argument) {
          if (classof(argument) === 'Symbol') throw new TypeError('Cannot convert a Symbol value to a string');
          return $String(argument);
        };
        /***/ }),

      /***/ 3691:
      /***/ (function (module) {
        'use strict';

        const $String = String;

        module.exports = function (argument) {
          try {
            return $String(argument);
          } catch (error) {
            return 'Object';
          }
        };
        /***/ }),

      /***/ 4630:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const uncurryThis = __webpack_require__(8844);

        let id = 0;
        const postfix = Math.random();
        const toString = uncurryThis(1.0.toString);

        module.exports = function (key) {
          return `Symbol(${key === undefined ? '' : key})_${toString(++id + postfix, 36)}`;
        };
        /***/ }),

      /***/ 9525:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        /* eslint-disable es/no-symbol -- required for testing */
        const NATIVE_SYMBOL = __webpack_require__(146);

        module.exports = NATIVE_SYMBOL
  && !Symbol.sham
  && typeof Symbol.iterator === 'symbol';
        /***/ }),

      /***/ 5648:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const fails = __webpack_require__(3689);

        // V8 ~ Chrome 36-
        // https://bugs.chromium.org/p/v8/issues/detail?id=3334
        module.exports = DESCRIPTORS && fails(() =>
          // eslint-disable-next-line es/no-object-defineproperty -- required for testing
          Object.defineProperty(() => { /* empty */ }, 'prototype', {
            value: 42,
            writable: false,
          }).prototype !== 42);
        /***/ }),

      /***/ 9834:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);
        const isCallable = __webpack_require__(9985);

        const { WeakMap } = global;

        module.exports = isCallable(WeakMap) && /native code/.test(String(WeakMap));
        /***/ }),

      /***/ 5405:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const path = __webpack_require__(496);
        const hasOwn = __webpack_require__(6812);
        const wrappedWellKnownSymbolModule = __webpack_require__(6145);
        const defineProperty = (__webpack_require__(2560).f);

        module.exports = function (NAME) {
          const Symbol = path.Symbol || (path.Symbol = {});
          if (!hasOwn(Symbol, NAME)) defineProperty(Symbol, NAME, {
            value: wrappedWellKnownSymbolModule.f(NAME),
          });
        };
        /***/ }),

      /***/ 6145:
      /***/ (function (__unused_webpack_module, exports, __webpack_require__) {
        'use strict';

        const wellKnownSymbol = __webpack_require__(4201);

        exports.f = wellKnownSymbol;
        /***/ }),

      /***/ 4201:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);
        const shared = __webpack_require__(3430);
        const hasOwn = __webpack_require__(6812);
        const uid = __webpack_require__(4630);
        const NATIVE_SYMBOL = __webpack_require__(146);
        const USE_SYMBOL_AS_UID = __webpack_require__(9525);

        const { Symbol } = global;
        const WellKnownSymbolsStore = shared('wks');
        const createWellKnownSymbol = USE_SYMBOL_AS_UID ? Symbol.for || Symbol : Symbol && Symbol.withoutSetter || uid;

        module.exports = function (name) {
          if (!hasOwn(WellKnownSymbolsStore, name)) {
            WellKnownSymbolsStore[name] = NATIVE_SYMBOL && hasOwn(Symbol, name)
              ? Symbol[name]
              : createWellKnownSymbol(`Symbol.${name}`);
          } return WellKnownSymbolsStore[name];
        };
        /***/ }),

      /***/ 4338:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const fails = __webpack_require__(3689);
        const isArray = __webpack_require__(2297);
        const isObject = __webpack_require__(8999);
        const toObject = __webpack_require__(690);
        const lengthOfArrayLike = __webpack_require__(6310);
        const doesNotExceedSafeInteger = __webpack_require__(5565);
        const createProperty = __webpack_require__(6522);
        const arraySpeciesCreate = __webpack_require__(7120);
        const arrayMethodHasSpeciesSupport = __webpack_require__(9042);
        const wellKnownSymbol = __webpack_require__(4201);
        const V8_VERSION = __webpack_require__(3615);

        const IS_CONCAT_SPREADABLE = wellKnownSymbol('isConcatSpreadable');

        // We can't use this feature detection in V8 since it causes
        // deoptimization and serious performance degradation
        // https://github.com/zloirock/core-js/issues/679
        const IS_CONCAT_SPREADABLE_SUPPORT = V8_VERSION >= 51 || !fails(() => {
          const array = [];
          array[IS_CONCAT_SPREADABLE] = false;
          return array.concat()[0] !== array;
        });

        const isConcatSpreadable = function (O) {
          if (!isObject(O)) return false;
          const spreadable = O[IS_CONCAT_SPREADABLE];
          return spreadable !== undefined ? !!spreadable : isArray(O);
        };

        const FORCED = !IS_CONCAT_SPREADABLE_SUPPORT || !arrayMethodHasSpeciesSupport('concat');

        // `Array.prototype.concat` method
        // https://tc39.es/ecma262/#sec-array.prototype.concat
        // with adding support of @@isConcatSpreadable and @@species
        $({ target: 'Array', proto: true, arity: 1, forced: FORCED }, {
          // eslint-disable-next-line no-unused-vars -- required for `.length`
          concat: function concat(arg) {
            const O = toObject(this);
            const A = arraySpeciesCreate(O, 0);
            let n = 0;
            let i; let k; let length; let len; let E;
            for (i = -1, length = arguments.length; i < length; i++) {
              E = i === -1 ? O : arguments[i];
              if (isConcatSpreadable(E)) {
                len = lengthOfArrayLike(E);
                doesNotExceedSafeInteger(n + len);
                for (k = 0; k < len; k++, n++) if (k in E) createProperty(A, n, E[k]);
              } else {
                doesNotExceedSafeInteger(n + 1);
                createProperty(A, n++, E);
              }
            }
            A.length = n;
            return A;
          },
        });
        /***/ }),

      /***/ 7895:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const fill = __webpack_require__(2872);
        const addToUnscopables = __webpack_require__(7370);

        // `Array.prototype.fill` method
        // https://tc39.es/ecma262/#sec-array.prototype.fill
        $({ target: 'Array', proto: true }, {
          fill,
        });

        // https://tc39.es/ecma262/#sec-array.prototype-@@unscopables
        addToUnscopables('fill');
        /***/ }),

      /***/ 8077:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const $filter = (__webpack_require__(2960).filter);
        const arrayMethodHasSpeciesSupport = __webpack_require__(9042);

        const HAS_SPECIES_SUPPORT = arrayMethodHasSpeciesSupport('filter');

        // `Array.prototype.filter` method
        // https://tc39.es/ecma262/#sec-array.prototype.filter
        // with adding support of @@species
        $({ target: 'Array', proto: true, forced: !HAS_SPECIES_SUPPORT }, {
          filter: function filter(callbackfn /* , thisArg */) {
            return $filter(this, callbackfn, arguments.length > 1 ? arguments[1] : undefined);
          },
        });
        /***/ }),

      /***/ 9772:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const $findIndex = (__webpack_require__(2960).findIndex);
        const addToUnscopables = __webpack_require__(7370);

        const FIND_INDEX = 'findIndex';
        let SKIPS_HOLES = true;

        // Shouldn't skip holes
        // eslint-disable-next-line es/no-array-prototype-findindex -- testing
        if (FIND_INDEX in []) Array(1)[FIND_INDEX](() => {
          SKIPS_HOLES = false;
        });

        // `Array.prototype.findIndex` method
        // https://tc39.es/ecma262/#sec-array.prototype.findindex
        $({ target: 'Array', proto: true, forced: SKIPS_HOLES }, {
          findIndex: function findIndex(callbackfn /* , that = undefined */) {
            return $findIndex(this, callbackfn, arguments.length > 1 ? arguments[1] : undefined);
          },
        });

        // https://tc39.es/ecma262/#sec-array.prototype-@@unscopables
        addToUnscopables(FIND_INDEX);
        /***/ }),

      /***/ 6801:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const $includes = (__webpack_require__(4328).includes);
        const fails = __webpack_require__(3689);
        const addToUnscopables = __webpack_require__(7370);

        // FF99+ bug
        const BROKEN_ON_SPARSE = fails(() =>
          // eslint-disable-next-line es/no-array-prototype-includes -- detection
          !Array(1).includes());

        // `Array.prototype.includes` method
        // https://tc39.es/ecma262/#sec-array.prototype.includes
        $({ target: 'Array', proto: true, forced: BROKEN_ON_SPARSE }, {
          includes: function includes(el /* , fromIndex = 0 */) {
            return $includes(this, el, arguments.length > 1 ? arguments[1] : undefined);
          },
        });

        // https://tc39.es/ecma262/#sec-array.prototype-@@unscopables
        addToUnscopables('includes');
        /***/ }),

      /***/ 752:
      /***/ (function (module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const toIndexedObject = __webpack_require__(5290);
        const addToUnscopables = __webpack_require__(7370);
        const Iterators = __webpack_require__(9478);
        const InternalStateModule = __webpack_require__(618);
        const defineProperty = (__webpack_require__(2560).f);
        const defineIterator = __webpack_require__(1934);
        const createIterResultObject = __webpack_require__(7807);
        const IS_PURE = __webpack_require__(3931);
        const DESCRIPTORS = __webpack_require__(7697);

        const ARRAY_ITERATOR = 'Array Iterator';
        const setInternalState = InternalStateModule.set;
        const getInternalState = InternalStateModule.getterFor(ARRAY_ITERATOR);

        // `Array.prototype.entries` method
        // https://tc39.es/ecma262/#sec-array.prototype.entries
        // `Array.prototype.keys` method
        // https://tc39.es/ecma262/#sec-array.prototype.keys
        // `Array.prototype.values` method
        // https://tc39.es/ecma262/#sec-array.prototype.values
        // `Array.prototype[@@iterator]` method
        // https://tc39.es/ecma262/#sec-array.prototype-@@iterator
        // `CreateArrayIterator` internal method
        // https://tc39.es/ecma262/#sec-createarrayiterator
        module.exports = defineIterator(Array, 'Array', function (iterated, kind) {
          setInternalState(this, {
            type: ARRAY_ITERATOR,
            target: toIndexedObject(iterated), // target
            index: 0,                          // next index
            kind,                         // kind
          });
          // `%ArrayIteratorPrototype%.next` method
          // https://tc39.es/ecma262/#sec-%arrayiteratorprototype%.next
        }, function () {
          const state = getInternalState(this);
          const { target } = state;
          const index = state.index++;
          if (!target || index >= target.length) {
            state.target = undefined;
            return createIterResultObject(undefined, true);
          }
          switch (state.kind) {
            case 'keys': return createIterResultObject(index, false);
            case 'values': return createIterResultObject(target[index], false);
          } return createIterResultObject([index, target[index]], false);
        }, 'values');

        // argumentsList[@@iterator] is %ArrayProto_values%
        // https://tc39.es/ecma262/#sec-createunmappedargumentsobject
        // https://tc39.es/ecma262/#sec-createmappedargumentsobject
        const values = Iterators.Arguments = Iterators.Array;

        // https://tc39.es/ecma262/#sec-array.prototype-@@unscopables
        addToUnscopables('keys');
        addToUnscopables('values');
        addToUnscopables('entries');

        // V8 ~ Chrome 45- bug
        if (!IS_PURE && DESCRIPTORS && values.name !== 'values') try {
          defineProperty(values, 'name', { value: 'values' });
        } catch (error) { /* empty */ }
        /***/ }),

      /***/ 6203:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const uncurryThis = __webpack_require__(8844);
        const IndexedObject = __webpack_require__(4413);
        const toIndexedObject = __webpack_require__(5290);
        const arrayMethodIsStrict = __webpack_require__(6834);

        const nativeJoin = uncurryThis([].join);

        const ES3_STRINGS = IndexedObject !== Object;
        const FORCED = ES3_STRINGS || !arrayMethodIsStrict('join', ',');

        // `Array.prototype.join` method
        // https://tc39.es/ecma262/#sec-array.prototype.join
        $({ target: 'Array', proto: true, forced: FORCED }, {
          join: function join(separator) {
            return nativeJoin(toIndexedObject(this), separator === undefined ? ',' : separator);
          },
        });
        /***/ }),

      /***/ 886:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const $map = (__webpack_require__(2960).map);
        const arrayMethodHasSpeciesSupport = __webpack_require__(9042);

        const HAS_SPECIES_SUPPORT = arrayMethodHasSpeciesSupport('map');

        // `Array.prototype.map` method
        // https://tc39.es/ecma262/#sec-array.prototype.map
        // with adding support of @@species
        $({ target: 'Array', proto: true, forced: !HAS_SPECIES_SUPPORT }, {
          map: function map(callbackfn /* , thisArg */) {
            return $map(this, callbackfn, arguments.length > 1 ? arguments[1] : undefined);
          },
        });
        /***/ }),

      /***/ 2506:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const toObject = __webpack_require__(690);
        const toAbsoluteIndex = __webpack_require__(7578);
        const toIntegerOrInfinity = __webpack_require__(8700);
        const lengthOfArrayLike = __webpack_require__(6310);
        const setArrayLength = __webpack_require__(5649);
        const doesNotExceedSafeInteger = __webpack_require__(5565);
        const arraySpeciesCreate = __webpack_require__(7120);
        const createProperty = __webpack_require__(6522);
        const deletePropertyOrThrow = __webpack_require__(8494);
        const arrayMethodHasSpeciesSupport = __webpack_require__(9042);

        const HAS_SPECIES_SUPPORT = arrayMethodHasSpeciesSupport('splice');

        const { max } = Math;
        const { min } = Math;

        // `Array.prototype.splice` method
        // https://tc39.es/ecma262/#sec-array.prototype.splice
        // with adding support of @@species
        $({ target: 'Array', proto: true, forced: !HAS_SPECIES_SUPPORT }, {
          splice: function splice(start, deleteCount /* , ...items */) {
            const O = toObject(this);
            const len = lengthOfArrayLike(O);
            const actualStart = toAbsoluteIndex(start, len);
            const argumentsLength = arguments.length;
            let insertCount; let actualDeleteCount; let A; let k; let from; let to;
            if (argumentsLength === 0) {
              insertCount = actualDeleteCount = 0;
            } else if (argumentsLength === 1) {
              insertCount = 0;
              actualDeleteCount = len - actualStart;
            } else {
              insertCount = argumentsLength - 2;
              actualDeleteCount = min(max(toIntegerOrInfinity(deleteCount), 0), len - actualStart);
            }
            doesNotExceedSafeInteger(len + insertCount - actualDeleteCount);
            A = arraySpeciesCreate(O, actualDeleteCount);
            for (k = 0; k < actualDeleteCount; k++) {
              from = actualStart + k;
              if (from in O) createProperty(A, k, O[from]);
            }
            A.length = actualDeleteCount;
            if (insertCount < actualDeleteCount) {
              for (k = actualStart; k < len - actualDeleteCount; k++) {
                from = k + actualDeleteCount;
                to = k + insertCount;
                if (from in O) O[to] = O[from];
                else deletePropertyOrThrow(O, to);
              }
              for (k = len; k > len - actualDeleteCount + insertCount; k--) deletePropertyOrThrow(O, k - 1);
            } else if (insertCount > actualDeleteCount) {
              for (k = len - actualDeleteCount; k > actualStart; k--) {
                from = k + actualDeleteCount - 1;
                to = k + insertCount - 1;
                if (from in O) O[to] = O[from];
                else deletePropertyOrThrow(O, to);
              }
            }
            for (k = 0; k < insertCount; k++) {
              O[k + actualStart] = arguments[k + 2];
            }
            setArrayLength(O, len - actualDeleteCount + insertCount);
            return A;
          },
        });
        /***/ }),

      /***/ 4284:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const DESCRIPTORS = __webpack_require__(7697);
        const FUNCTION_NAME_EXISTS = (__webpack_require__(1236).EXISTS);
        const uncurryThis = __webpack_require__(8844);
        const defineBuiltInAccessor = __webpack_require__(2148);

        const FunctionPrototype = Function.prototype;
        const functionToString = uncurryThis(FunctionPrototype.toString);
        const nameRE = /function\b(?:\s|\/\*[\S\s]*?\*\/|\/\/[^\n\r]*[\n\r]+)*([^\s(/]*)/;
        const regExpExec = uncurryThis(nameRE.exec);
        const NAME = 'name';

        // Function instances `.name` property
        // https://tc39.es/ecma262/#sec-function-instances-name
        if (DESCRIPTORS && !FUNCTION_NAME_EXISTS) {
          defineBuiltInAccessor(FunctionPrototype, NAME, {
            configurable: true,
            get() {
              try {
                return regExpExec(nameRE, functionToString(this))[1];
              } catch (error) {
                return '';
              }
            },
          });
        }
        /***/ }),

      /***/ 8324:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const getBuiltIn = __webpack_require__(6058);
        const apply = __webpack_require__(1735);
        const call = __webpack_require__(2615);
        const uncurryThis = __webpack_require__(8844);
        const fails = __webpack_require__(3689);
        const isCallable = __webpack_require__(9985);
        const isSymbol = __webpack_require__(734);
        const arraySlice = __webpack_require__(6004);
        const getReplacerFunction = __webpack_require__(2643);
        const NATIVE_SYMBOL = __webpack_require__(146);

        const $String = String;
        const $stringify = getBuiltIn('JSON', 'stringify');
        const exec = uncurryThis(/./.exec);
        const charAt = uncurryThis(''.charAt);
        const charCodeAt = uncurryThis(''.charCodeAt);
        const replace = uncurryThis(''.replace);
        const numberToString = uncurryThis(1.0.toString);

        const tester = /[\uD800-\uDFFF]/g;
        const low = /^[\uD800-\uDBFF]$/;
        const hi = /^[\uDC00-\uDFFF]$/;

        const WRONG_SYMBOLS_CONVERSION = !NATIVE_SYMBOL || fails(() => {
          const symbol = getBuiltIn('Symbol')('stringify detection');
          // MS Edge converts symbol values to JSON as {}
          return $stringify([symbol]) !== '[null]'
    // WebKit converts symbol values to JSON as null
    || $stringify({ a: symbol }) !== '{}'
    // V8 throws on boxed symbols
    || $stringify(Object(symbol)) !== '{}';
        });

        // https://github.com/tc39/proposal-well-formed-stringify
        const ILL_FORMED_UNICODE = fails(() => $stringify('\uDF06\uD834') !== '"\\udf06\\ud834"'
    || $stringify('\uDEAD') !== '"\\udead"');

        const stringifyWithSymbolsFix = function (it, replacer) {
          const args = arraySlice(arguments);
          const $replacer = getReplacerFunction(replacer);
          if (!isCallable($replacer) && (it === undefined || isSymbol(it))) return; // IE8 returns string on undefined
          args[1] = function (key, value) {
            // some old implementations (like WebKit) could pass numbers as keys
            if (isCallable($replacer)) value = call($replacer, this, $String(key), value);
            if (!isSymbol(value)) return value;
          };
          return apply($stringify, null, args);
        };

        const fixIllFormed = function (match, offset, string) {
          const prev = charAt(string, offset - 1);
          const next = charAt(string, offset + 1);
          if ((exec(low, match) && !exec(hi, next)) || (exec(hi, match) && !exec(low, prev))) {
            return `\\u${numberToString(charCodeAt(match, 0), 16)}`;
          } return match;
        };

        if ($stringify) {
          // `JSON.stringify` method
          // https://tc39.es/ecma262/#sec-json.stringify
          $({ target: 'JSON', stat: true, arity: 3, forced: WRONG_SYMBOLS_CONVERSION || ILL_FORMED_UNICODE }, {
            // eslint-disable-next-line no-unused-vars -- required for `.length`
            stringify: function stringify(it, replacer, space) {
              const args = arraySlice(arguments);
              const result = apply(WRONG_SYMBOLS_CONVERSION ? stringifyWithSymbolsFix : $stringify, null, args);
              return ILL_FORMED_UNICODE && typeof result === 'string' ? replace(result, tester, fixIllFormed) : result;
            },
          });
        }
        /***/ }),

      /***/ 429:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const assign = __webpack_require__(5394);

        // `Object.assign` method
        // https://tc39.es/ecma262/#sec-object.assign
        // eslint-disable-next-line es/no-object-assign -- required for testing
        $({ target: 'Object', stat: true, arity: 2, forced: Object.assign !== assign }, {
          assign,
        });
        /***/ }),

      /***/ 1919:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const fails = __webpack_require__(3689);
        const toIndexedObject = __webpack_require__(5290);
        const nativeGetOwnPropertyDescriptor = (__webpack_require__(2474).f);
        const DESCRIPTORS = __webpack_require__(7697);

        const FORCED = !DESCRIPTORS || fails(() => {
          nativeGetOwnPropertyDescriptor(1);
        });

        // `Object.getOwnPropertyDescriptor` method
        // https://tc39.es/ecma262/#sec-object.getownpropertydescriptor
        $({ target: 'Object', stat: true, forced: FORCED, sham: !DESCRIPTORS }, {
          getOwnPropertyDescriptor: function getOwnPropertyDescriptor(it, key) {
            return nativeGetOwnPropertyDescriptor(toIndexedObject(it), key);
          },
        });
        /***/ }),

      /***/ 9474:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const DESCRIPTORS = __webpack_require__(7697);
        const ownKeys = __webpack_require__(9152);
        const toIndexedObject = __webpack_require__(5290);
        const getOwnPropertyDescriptorModule = __webpack_require__(2474);
        const createProperty = __webpack_require__(6522);

        // `Object.getOwnPropertyDescriptors` method
        // https://tc39.es/ecma262/#sec-object.getownpropertydescriptors
        $({ target: 'Object', stat: true, sham: !DESCRIPTORS }, {
          getOwnPropertyDescriptors: function getOwnPropertyDescriptors(object) {
            const O = toIndexedObject(object);
            const getOwnPropertyDescriptor = getOwnPropertyDescriptorModule.f;
            const keys = ownKeys(O);
            const result = {};
            let index = 0;
            let key; let descriptor;
            while (keys.length > index) {
              descriptor = getOwnPropertyDescriptor(O, key = keys[index++]);
              if (descriptor !== undefined) createProperty(result, key, descriptor);
            }
            return result;
          },
        });
        /***/ }),

      /***/ 9434:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const NATIVE_SYMBOL = __webpack_require__(146);
        const fails = __webpack_require__(3689);
        const getOwnPropertySymbolsModule = __webpack_require__(7518);
        const toObject = __webpack_require__(690);

        // V8 ~ Chrome 38 and 39 `Object.getOwnPropertySymbols` fails on primitives
        // https://bugs.chromium.org/p/v8/issues/detail?id=3443
        const FORCED = !NATIVE_SYMBOL || fails(() => {
          getOwnPropertySymbolsModule.f(1);
        });

        // `Object.getOwnPropertySymbols` method
        // https://tc39.es/ecma262/#sec-object.getownpropertysymbols
        $({ target: 'Object', stat: true, forced: FORCED }, {
          getOwnPropertySymbols: function getOwnPropertySymbols(it) {
            const $getOwnPropertySymbols = getOwnPropertySymbolsModule.f;
            return $getOwnPropertySymbols ? $getOwnPropertySymbols(toObject(it)) : [];
          },
        });
        /***/ }),

      /***/ 9358:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const toObject = __webpack_require__(690);
        const nativeKeys = __webpack_require__(300);
        const fails = __webpack_require__(3689);

        const FAILS_ON_PRIMITIVES = fails(() => {
          nativeKeys(1);
        });

        // `Object.keys` method
        // https://tc39.es/ecma262/#sec-object.keys
        $({ target: 'Object', stat: true, forced: FAILS_ON_PRIMITIVES }, {
          keys: function keys(it) {
            return nativeKeys(toObject(it));
          },
        });
        /***/ }),

      /***/ 228:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const TO_STRING_TAG_SUPPORT = __webpack_require__(3043);
        const defineBuiltIn = __webpack_require__(1880);
        const toString = __webpack_require__(5073);

        // `Object.prototype.toString` method
        // https://tc39.es/ecma262/#sec-object.prototype.tostring
        if (!TO_STRING_TAG_SUPPORT) {
          defineBuiltIn(Object.prototype, 'toString', toString, { unsafe: true });
        }
        /***/ }),

      /***/ 9707:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);

        // `Reflect.has` method
        // https://tc39.es/ecma262/#sec-reflect.has
        $({ target: 'Reflect', stat: true }, {
          has: function has(target, propertyKey) {
            return propertyKey in target;
          },
        });
        /***/ }),

      /***/ 1694:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const { charAt } = __webpack_require__(730);
        const toString = __webpack_require__(4327);
        const InternalStateModule = __webpack_require__(618);
        const defineIterator = __webpack_require__(1934);
        const createIterResultObject = __webpack_require__(7807);

        const STRING_ITERATOR = 'String Iterator';
        const setInternalState = InternalStateModule.set;
        const getInternalState = InternalStateModule.getterFor(STRING_ITERATOR);

        // `String.prototype[@@iterator]` method
        // https://tc39.es/ecma262/#sec-string.prototype-@@iterator
        defineIterator(String, 'String', function (iterated) {
          setInternalState(this, {
            type: STRING_ITERATOR,
            string: toString(iterated),
            index: 0,
          });
          // `%StringIteratorPrototype%.next` method
          // https://tc39.es/ecma262/#sec-%stringiteratorprototype%.next
        }, function next() {
          const state = getInternalState(this);
          const { string } = state;
          const { index } = state;
          let point;
          if (index >= string.length) return createIterResultObject(undefined, true);
          point = charAt(string, index);
          state.index += point.length;
          return createIterResultObject(point, false);
        });
        /***/ }),

      /***/ 7855:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const global = __webpack_require__(9037);
        const call = __webpack_require__(2615);
        const uncurryThis = __webpack_require__(8844);
        const IS_PURE = __webpack_require__(3931);
        const DESCRIPTORS = __webpack_require__(7697);
        const NATIVE_SYMBOL = __webpack_require__(146);
        const fails = __webpack_require__(3689);
        const hasOwn = __webpack_require__(6812);
        const isPrototypeOf = __webpack_require__(3622);
        const anObject = __webpack_require__(5027);
        const toIndexedObject = __webpack_require__(5290);
        const toPropertyKey = __webpack_require__(8360);
        const $toString = __webpack_require__(4327);
        const createPropertyDescriptor = __webpack_require__(5684);
        const nativeObjectCreate = __webpack_require__(5391);
        const objectKeys = __webpack_require__(300);
        const getOwnPropertyNamesModule = __webpack_require__(2741);
        const getOwnPropertyNamesExternal = __webpack_require__(6062);
        const getOwnPropertySymbolsModule = __webpack_require__(7518);
        const getOwnPropertyDescriptorModule = __webpack_require__(2474);
        const definePropertyModule = __webpack_require__(2560);
        const definePropertiesModule = __webpack_require__(8920);
        const propertyIsEnumerableModule = __webpack_require__(9556);
        const defineBuiltIn = __webpack_require__(1880);
        const defineBuiltInAccessor = __webpack_require__(2148);
        const shared = __webpack_require__(3430);
        const sharedKey = __webpack_require__(2713);
        const hiddenKeys = __webpack_require__(7248);
        const uid = __webpack_require__(4630);
        const wellKnownSymbol = __webpack_require__(4201);
        const wrappedWellKnownSymbolModule = __webpack_require__(6145);
        const defineWellKnownSymbol = __webpack_require__(5405);
        const defineSymbolToPrimitive = __webpack_require__(3032);
        const setToStringTag = __webpack_require__(5997);
        const InternalStateModule = __webpack_require__(618);
        const $forEach = (__webpack_require__(2960).forEach);

        const HIDDEN = sharedKey('hidden');
        const SYMBOL = 'Symbol';
        const PROTOTYPE = 'prototype';

        const setInternalState = InternalStateModule.set;
        const getInternalState = InternalStateModule.getterFor(SYMBOL);

        const ObjectPrototype = Object[PROTOTYPE];
        let $Symbol = global.Symbol;
        let SymbolPrototype = $Symbol && $Symbol[PROTOTYPE];
        const { RangeError } = global;
        const { TypeError } = global;
        const { QObject } = global;
        const nativeGetOwnPropertyDescriptor = getOwnPropertyDescriptorModule.f;
        const nativeDefineProperty = definePropertyModule.f;
        const nativeGetOwnPropertyNames = getOwnPropertyNamesExternal.f;
        const nativePropertyIsEnumerable = propertyIsEnumerableModule.f;
        const push = uncurryThis([].push);

        const AllSymbols = shared('symbols');
        const ObjectPrototypeSymbols = shared('op-symbols');
        const WellKnownSymbolsStore = shared('wks');

        // Don't use setters in Qt Script, https://github.com/zloirock/core-js/issues/173
        let USE_SETTER = !QObject || !QObject[PROTOTYPE] || !QObject[PROTOTYPE].findChild;

        // fallback for old Android, https://code.google.com/p/v8/issues/detail?id=687
        const fallbackDefineProperty = function (O, P, Attributes) {
          const ObjectPrototypeDescriptor = nativeGetOwnPropertyDescriptor(ObjectPrototype, P);
          if (ObjectPrototypeDescriptor) delete ObjectPrototype[P];
          nativeDefineProperty(O, P, Attributes);
          if (ObjectPrototypeDescriptor && O !== ObjectPrototype) {
            nativeDefineProperty(ObjectPrototype, P, ObjectPrototypeDescriptor);
          }
        };

        const setSymbolDescriptor = DESCRIPTORS && fails(() => nativeObjectCreate(nativeDefineProperty({}, 'a', {
          get() {
            return nativeDefineProperty(this, 'a', { value: 7 }).a;
          },
        })).a !== 7) ? fallbackDefineProperty : nativeDefineProperty;

        const wrap = function (tag, description) {
          const symbol = AllSymbols[tag] = nativeObjectCreate(SymbolPrototype);
          setInternalState(symbol, {
            type: SYMBOL,
            tag,
            description,
          });
          if (!DESCRIPTORS) symbol.description = description;
          return symbol;
        };

        var $defineProperty = function defineProperty(O, P, Attributes) {
          if (O === ObjectPrototype) $defineProperty(ObjectPrototypeSymbols, P, Attributes);
          anObject(O);
          const key = toPropertyKey(P);
          anObject(Attributes);
          if (hasOwn(AllSymbols, key)) {
            if (!Attributes.enumerable) {
              if (!hasOwn(O, HIDDEN)) nativeDefineProperty(O, HIDDEN, createPropertyDescriptor(1, {}));
              O[HIDDEN][key] = true;
            } else {
              if (hasOwn(O, HIDDEN) && O[HIDDEN][key]) O[HIDDEN][key] = false;
              Attributes = nativeObjectCreate(Attributes, { enumerable: createPropertyDescriptor(0, false) });
            } return setSymbolDescriptor(O, key, Attributes);
          } return nativeDefineProperty(O, key, Attributes);
        };

        const $defineProperties = function defineProperties(O, Properties) {
          anObject(O);
          const properties = toIndexedObject(Properties);
          const keys = objectKeys(properties).concat($getOwnPropertySymbols(properties));
          $forEach(keys, (key) => {
            if (!DESCRIPTORS || call($propertyIsEnumerable, properties, key)) $defineProperty(O, key, properties[key]);
          });
          return O;
        };

        const $create = function create(O, Properties) {
          return Properties === undefined ? nativeObjectCreate(O) : $defineProperties(nativeObjectCreate(O), Properties);
        };

        var $propertyIsEnumerable = function propertyIsEnumerable(V) {
          const P = toPropertyKey(V);
          const enumerable = call(nativePropertyIsEnumerable, this, P);
          if (this === ObjectPrototype && hasOwn(AllSymbols, P) && !hasOwn(ObjectPrototypeSymbols, P)) return false;
          return enumerable || !hasOwn(this, P) || !hasOwn(AllSymbols, P) || hasOwn(this, HIDDEN) && this[HIDDEN][P]
            ? enumerable : true;
        };

        const $getOwnPropertyDescriptor = function getOwnPropertyDescriptor(O, P) {
          const it = toIndexedObject(O);
          const key = toPropertyKey(P);
          if (it === ObjectPrototype && hasOwn(AllSymbols, key) && !hasOwn(ObjectPrototypeSymbols, key)) return;
          const descriptor = nativeGetOwnPropertyDescriptor(it, key);
          if (descriptor && hasOwn(AllSymbols, key) && !(hasOwn(it, HIDDEN) && it[HIDDEN][key])) {
            descriptor.enumerable = true;
          }
          return descriptor;
        };

        const $getOwnPropertyNames = function getOwnPropertyNames(O) {
          const names = nativeGetOwnPropertyNames(toIndexedObject(O));
          const result = [];
          $forEach(names, (key) => {
            if (!hasOwn(AllSymbols, key) && !hasOwn(hiddenKeys, key)) push(result, key);
          });
          return result;
        };

        var $getOwnPropertySymbols = function (O) {
          const IS_OBJECT_PROTOTYPE = O === ObjectPrototype;
          const names = nativeGetOwnPropertyNames(IS_OBJECT_PROTOTYPE ? ObjectPrototypeSymbols : toIndexedObject(O));
          const result = [];
          $forEach(names, (key) => {
            if (hasOwn(AllSymbols, key) && (!IS_OBJECT_PROTOTYPE || hasOwn(ObjectPrototype, key))) {
              push(result, AllSymbols[key]);
            }
          });
          return result;
        };

        // `Symbol` constructor
        // https://tc39.es/ecma262/#sec-symbol-constructor
        if (!NATIVE_SYMBOL) {
          $Symbol = function Symbol() {
            if (isPrototypeOf(SymbolPrototype, this)) throw new TypeError('Symbol is not a constructor');
            const description = !arguments.length || arguments[0] === undefined ? undefined : $toString(arguments[0]);
            const tag = uid(description);
            var setter = function (value) {
              const $this = this === undefined ? global : this;
              if ($this === ObjectPrototype) call(setter, ObjectPrototypeSymbols, value);
              if (hasOwn($this, HIDDEN) && hasOwn($this[HIDDEN], tag)) $this[HIDDEN][tag] = false;
              const descriptor = createPropertyDescriptor(1, value);
              try {
                setSymbolDescriptor($this, tag, descriptor);
              } catch (error) {
                if (!(error instanceof RangeError)) throw error;
                fallbackDefineProperty($this, tag, descriptor);
              }
            };
            if (DESCRIPTORS && USE_SETTER) setSymbolDescriptor(ObjectPrototype, tag, { configurable: true, set: setter });
            return wrap(tag, description);
          };

          SymbolPrototype = $Symbol[PROTOTYPE];

          defineBuiltIn(SymbolPrototype, 'toString', function toString() {
            return getInternalState(this).tag;
          });

          defineBuiltIn($Symbol, 'withoutSetter', description => wrap(uid(description), description));

          propertyIsEnumerableModule.f = $propertyIsEnumerable;
          definePropertyModule.f = $defineProperty;
          definePropertiesModule.f = $defineProperties;
          getOwnPropertyDescriptorModule.f = $getOwnPropertyDescriptor;
          getOwnPropertyNamesModule.f = getOwnPropertyNamesExternal.f = $getOwnPropertyNames;
          getOwnPropertySymbolsModule.f = $getOwnPropertySymbols;

          wrappedWellKnownSymbolModule.f = function (name) {
            return wrap(wellKnownSymbol(name), name);
          };

          if (DESCRIPTORS) {
            // https://github.com/tc39/proposal-Symbol-description
            defineBuiltInAccessor(SymbolPrototype, 'description', {
              configurable: true,
              get: function description() {
                return getInternalState(this).description;
              },
            });
            if (!IS_PURE) {
              defineBuiltIn(ObjectPrototype, 'propertyIsEnumerable', $propertyIsEnumerable, { unsafe: true });
            }
          }
        }

        $({ global: true, constructor: true, wrap: true, forced: !NATIVE_SYMBOL, sham: !NATIVE_SYMBOL }, {
          Symbol: $Symbol,
        });

        $forEach(objectKeys(WellKnownSymbolsStore), (name) => {
          defineWellKnownSymbol(name);
        });

        $({ target: SYMBOL, stat: true, forced: !NATIVE_SYMBOL }, {
          useSetter() {
            USE_SETTER = true;
          },
          useSimple() {
            USE_SETTER = false;
          },
        });

        $({ target: 'Object', stat: true, forced: !NATIVE_SYMBOL, sham: !DESCRIPTORS }, {
          // `Object.create` method
          // https://tc39.es/ecma262/#sec-object.create
          create: $create,
          // `Object.defineProperty` method
          // https://tc39.es/ecma262/#sec-object.defineproperty
          defineProperty: $defineProperty,
          // `Object.defineProperties` method
          // https://tc39.es/ecma262/#sec-object.defineproperties
          defineProperties: $defineProperties,
          // `Object.getOwnPropertyDescriptor` method
          // https://tc39.es/ecma262/#sec-object.getownpropertydescriptors
          getOwnPropertyDescriptor: $getOwnPropertyDescriptor,
        });

        $({ target: 'Object', stat: true, forced: !NATIVE_SYMBOL }, {
          // `Object.getOwnPropertyNames` method
          // https://tc39.es/ecma262/#sec-object.getownpropertynames
          getOwnPropertyNames: $getOwnPropertyNames,
        });

        // `Symbol.prototype[@@toPrimitive]` method
        // https://tc39.es/ecma262/#sec-symbol.prototype-@@toprimitive
        defineSymbolToPrimitive();

        // `Symbol.prototype[@@toStringTag]` property
        // https://tc39.es/ecma262/#sec-symbol.prototype-@@tostringtag
        setToStringTag($Symbol, SYMBOL);

        hiddenKeys[HIDDEN] = true;
        /***/ }),

      /***/ 3975:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const getBuiltIn = __webpack_require__(6058);
        const hasOwn = __webpack_require__(6812);
        const toString = __webpack_require__(4327);
        const shared = __webpack_require__(3430);
        const NATIVE_SYMBOL_REGISTRY = __webpack_require__(6549);

        const StringToSymbolRegistry = shared('string-to-symbol-registry');
        const SymbolToStringRegistry = shared('symbol-to-string-registry');

        // `Symbol.for` method
        // https://tc39.es/ecma262/#sec-symbol.for
        $({ target: 'Symbol', stat: true, forced: !NATIVE_SYMBOL_REGISTRY }, {
          for(key) {
            const string = toString(key);
            if (hasOwn(StringToSymbolRegistry, string)) return StringToSymbolRegistry[string];
            const symbol = getBuiltIn('Symbol')(string);
            StringToSymbolRegistry[string] = symbol;
            SymbolToStringRegistry[symbol] = string;
            return symbol;
          },
        });
        /***/ }),

      /***/ 9749:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        // TODO: Remove this module from `core-js@4` since it's split to modules listed below
        __webpack_require__(7855);
        __webpack_require__(3975);
        __webpack_require__(1445);
        __webpack_require__(8324);
        __webpack_require__(9434);
        /***/ }),

      /***/ 1445:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const $ = __webpack_require__(9989);
        const hasOwn = __webpack_require__(6812);
        const isSymbol = __webpack_require__(734);
        const tryToString = __webpack_require__(3691);
        const shared = __webpack_require__(3430);
        const NATIVE_SYMBOL_REGISTRY = __webpack_require__(6549);

        const SymbolToStringRegistry = shared('symbol-to-string-registry');

        // `Symbol.keyFor` method
        // https://tc39.es/ecma262/#sec-symbol.keyfor
        $({ target: 'Symbol', stat: true, forced: !NATIVE_SYMBOL_REGISTRY }, {
          keyFor: function keyFor(sym) {
            if (!isSymbol(sym)) throw new TypeError(`${tryToString(sym)} is not a symbol`);
            if (hasOwn(SymbolToStringRegistry, sym)) return SymbolToStringRegistry[sym];
          },
        });
        /***/ }),

      /***/ 5164:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const FREEZING = __webpack_require__(1594);
        const global = __webpack_require__(9037);
        const uncurryThis = __webpack_require__(8844);
        const defineBuiltIns = __webpack_require__(6045);
        const InternalMetadataModule = __webpack_require__(5375);
        const collection = __webpack_require__(319);
        const collectionWeak = __webpack_require__(637);
        const isObject = __webpack_require__(8999);
        const enforceInternalState = (__webpack_require__(618).enforce);
        const fails = __webpack_require__(3689);
        const NATIVE_WEAK_MAP = __webpack_require__(9834);

        const $Object = Object;
        // eslint-disable-next-line es/no-array-isarray -- safe
        const { isArray } = Array;
        // eslint-disable-next-line es/no-object-isextensible -- safe
        const { isExtensible } = $Object;
        // eslint-disable-next-line es/no-object-isfrozen -- safe
        const { isFrozen } = $Object;
        // eslint-disable-next-line es/no-object-issealed -- safe
        const { isSealed } = $Object;
        // eslint-disable-next-line es/no-object-freeze -- safe
        const { freeze } = $Object;
        // eslint-disable-next-line es/no-object-seal -- safe
        const { seal } = $Object;

        const FROZEN = {};
        const SEALED = {};
        const IS_IE11 = !global.ActiveXObject && 'ActiveXObject' in global;
        let InternalWeakMap;

        const wrapper = function (init) {
          return function WeakMap() {
            return init(this, arguments.length ? arguments[0] : undefined);
          };
        };

        // `WeakMap` constructor
        // https://tc39.es/ecma262/#sec-weakmap-constructor
        const $WeakMap = collection('WeakMap', wrapper, collectionWeak);
        const WeakMapPrototype = $WeakMap.prototype;
        const nativeSet = uncurryThis(WeakMapPrototype.set);

        // Chakra Edge bug: adding frozen arrays to WeakMap unfreeze them
        const hasMSEdgeFreezingBug = function () {
          return FREEZING && fails(() => {
            const frozenArray = freeze([]);
            nativeSet(new $WeakMap(), frozenArray, 1);
            return !isFrozen(frozenArray);
          });
        };

        // IE11 WeakMap frozen keys fix
        // We can't use feature detection because it crash some old IE builds
        // https://github.com/zloirock/core-js/issues/485
        if (NATIVE_WEAK_MAP) if (IS_IE11) {
          InternalWeakMap = collectionWeak.getConstructor(wrapper, 'WeakMap', true);
          InternalMetadataModule.enable();
          const nativeDelete = uncurryThis(WeakMapPrototype.delete);
          const nativeHas = uncurryThis(WeakMapPrototype.has);
          const nativeGet = uncurryThis(WeakMapPrototype.get);
          defineBuiltIns(WeakMapPrototype, {
            delete(key) {
              if (isObject(key) && !isExtensible(key)) {
                const state = enforceInternalState(this);
                if (!state.frozen) state.frozen = new InternalWeakMap();
                return nativeDelete(this, key) || state.frozen.delete(key);
              } return nativeDelete(this, key);
            },
            has: function has(key) {
              if (isObject(key) && !isExtensible(key)) {
                const state = enforceInternalState(this);
                if (!state.frozen) state.frozen = new InternalWeakMap();
                return nativeHas(this, key) || state.frozen.has(key);
              } return nativeHas(this, key);
            },
            get: function get(key) {
              if (isObject(key) && !isExtensible(key)) {
                const state = enforceInternalState(this);
                if (!state.frozen) state.frozen = new InternalWeakMap();
                return nativeHas(this, key) ? nativeGet(this, key) : state.frozen.get(key);
              } return nativeGet(this, key);
            },
            set: function set(key, value) {
              if (isObject(key) && !isExtensible(key)) {
                const state = enforceInternalState(this);
                if (!state.frozen) state.frozen = new InternalWeakMap();
                nativeHas(this, key) ? nativeSet(this, key, value) : state.frozen.set(key, value);
              } else nativeSet(this, key, value);
              return this;
            },
          });
          // Chakra Edge frozen keys fix
        } else if (hasMSEdgeFreezingBug()) {
          defineBuiltIns(WeakMapPrototype, {
            set: function set(key, value) {
              let arrayIntegrityLevel;
              if (isArray(key)) {
                if (isFrozen(key)) arrayIntegrityLevel = FROZEN;
                else if (isSealed(key)) arrayIntegrityLevel = SEALED;
              }
              nativeSet(this, key, value);
              if (arrayIntegrityLevel === FROZEN) freeze(key);
              if (arrayIntegrityLevel === SEALED) seal(key);
              return this;
            },
          });
        }
        /***/ }),

      /***/ 1090:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        // TODO: Remove this module from `core-js@4` since it's replaced to module below
        __webpack_require__(5164);
        /***/ }),

      /***/ 7522:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);
        const DOMIterables = __webpack_require__(6338);
        const DOMTokenListPrototype = __webpack_require__(3265);
        const forEach = __webpack_require__(7612);
        const createNonEnumerableProperty = __webpack_require__(5773);

        const handlePrototype = function (CollectionPrototype) {
          // some Chrome versions have non-configurable methods on DOMTokenList
          if (CollectionPrototype && CollectionPrototype.forEach !== forEach) try {
            createNonEnumerableProperty(CollectionPrototype, 'forEach', forEach);
          } catch (error) {
            CollectionPrototype.forEach = forEach;
          }
        };

        for (const COLLECTION_NAME in DOMIterables) {
          if (DOMIterables[COLLECTION_NAME]) {
            handlePrototype(global[COLLECTION_NAME] && global[COLLECTION_NAME].prototype);
          }
        }

        handlePrototype(DOMTokenListPrototype);
        /***/ }),

      /***/ 6265:
      /***/ (function (__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {
        'use strict';

        const global = __webpack_require__(9037);
        const DOMIterables = __webpack_require__(6338);
        const DOMTokenListPrototype = __webpack_require__(3265);
        const ArrayIteratorMethods = __webpack_require__(752);
        const createNonEnumerableProperty = __webpack_require__(5773);
        const wellKnownSymbol = __webpack_require__(4201);

        const ITERATOR = wellKnownSymbol('iterator');
        const TO_STRING_TAG = wellKnownSymbol('toStringTag');
        const ArrayValues = ArrayIteratorMethods.values;

        const handlePrototype = function (CollectionPrototype, COLLECTION_NAME) {
          if (CollectionPrototype) {
            // some Chrome versions have non-configurable methods on DOMTokenList
            if (CollectionPrototype[ITERATOR] !== ArrayValues) try {
              createNonEnumerableProperty(CollectionPrototype, ITERATOR, ArrayValues);
            } catch (error) {
              CollectionPrototype[ITERATOR] = ArrayValues;
            }
            if (!CollectionPrototype[TO_STRING_TAG]) {
              createNonEnumerableProperty(CollectionPrototype, TO_STRING_TAG, COLLECTION_NAME);
            }
            if (DOMIterables[COLLECTION_NAME]) for (const METHOD_NAME in ArrayIteratorMethods) {
              // some Chrome versions have non-configurable methods on DOMTokenList
              if (CollectionPrototype[METHOD_NAME] !== ArrayIteratorMethods[METHOD_NAME]) try {
                createNonEnumerableProperty(CollectionPrototype, METHOD_NAME, ArrayIteratorMethods[METHOD_NAME]);
              } catch (error) {
                CollectionPrototype[METHOD_NAME] = ArrayIteratorMethods[METHOD_NAME];
              }
            }
          }
        };

        for (const COLLECTION_NAME in DOMIterables) {
          handlePrototype(global[COLLECTION_NAME] && global[COLLECTION_NAME].prototype, COLLECTION_NAME);
        }

        handlePrototype(DOMTokenListPrototype, 'DOMTokenList');
        /***/ }),

      /***/ 4775:
      /***/ (function (module) {
        'use strict';
        module.exports = JSON.parse('{"$id":"https://raw.githubusercontent.com/ajv-validator/ajv/master/lib/refs/data.json#","description":"Meta-schema for $data reference (JSON AnySchema extension proposal)","type":"object","required":["$data"],"properties":{"$data":{"type":"string","anyOf":[{"format":"relative-json-pointer"},{"format":"json-pointer"}]}},"additionalProperties":false}');
        /***/ }),

      /***/ 98:
      /***/ (function (module) {
        'use strict';
        module.exports = JSON.parse('{"$schema":"http://json-schema.org/draft-07/schema#","$id":"http://json-schema.org/draft-07/schema#","title":"Core schema meta-schema","definitions":{"schemaArray":{"type":"array","minItems":1,"items":{"$ref":"#"}},"nonNegativeInteger":{"type":"integer","minimum":0},"nonNegativeIntegerDefault0":{"allOf":[{"$ref":"#/definitions/nonNegativeInteger"},{"default":0}]},"simpleTypes":{"enum":["array","boolean","integer","null","number","object","string"]},"stringArray":{"type":"array","items":{"type":"string"},"uniqueItems":true,"default":[]}},"type":["object","boolean"],"properties":{"$id":{"type":"string","format":"uri-reference"},"$schema":{"type":"string","format":"uri"},"$ref":{"type":"string","format":"uri-reference"},"$comment":{"type":"string"},"title":{"type":"string"},"description":{"type":"string"},"default":true,"readOnly":{"type":"boolean","default":false},"examples":{"type":"array","items":true},"multipleOf":{"type":"number","exclusiveMinimum":0},"maximum":{"type":"number"},"exclusiveMaximum":{"type":"number"},"minimum":{"type":"number"},"exclusiveMinimum":{"type":"number"},"maxLength":{"$ref":"#/definitions/nonNegativeInteger"},"minLength":{"$ref":"#/definitions/nonNegativeIntegerDefault0"},"pattern":{"type":"string","format":"regex"},"additionalItems":{"$ref":"#"},"items":{"anyOf":[{"$ref":"#"},{"$ref":"#/definitions/schemaArray"}],"default":true},"maxItems":{"$ref":"#/definitions/nonNegativeInteger"},"minItems":{"$ref":"#/definitions/nonNegativeIntegerDefault0"},"uniqueItems":{"type":"boolean","default":false},"contains":{"$ref":"#"},"maxProperties":{"$ref":"#/definitions/nonNegativeInteger"},"minProperties":{"$ref":"#/definitions/nonNegativeIntegerDefault0"},"required":{"$ref":"#/definitions/stringArray"},"additionalProperties":{"$ref":"#"},"definitions":{"type":"object","additionalProperties":{"$ref":"#"},"default":{}},"properties":{"type":"object","additionalProperties":{"$ref":"#"},"default":{}},"patternProperties":{"type":"object","additionalProperties":{"$ref":"#"},"propertyNames":{"format":"regex"},"default":{}},"dependencies":{"type":"object","additionalProperties":{"anyOf":[{"$ref":"#"},{"$ref":"#/definitions/stringArray"}]}},"propertyNames":{"$ref":"#"},"const":true,"enum":{"type":"array","items":true,"minItems":1,"uniqueItems":true},"type":{"anyOf":[{"$ref":"#/definitions/simpleTypes"},{"type":"array","items":{"$ref":"#/definitions/simpleTypes"},"minItems":1,"uniqueItems":true}]},"format":{"type":"string"},"contentMediaType":{"type":"string"},"contentEncoding":{"type":"string"},"if":{"$ref":"#"},"then":{"$ref":"#"},"else":{"$ref":"#"},"allOf":{"$ref":"#/definitions/schemaArray"},"anyOf":{"$ref":"#/definitions/schemaArray"},"oneOf":{"$ref":"#/definitions/schemaArray"},"not":{"$ref":"#"}},"default":true}');
        /***/ }),

      /** ****/ 	});
    /** **********************************************************************/
    /** ****/ 	// The module cache
    /** ****/ 	const __webpack_module_cache__ = {};
    /** ****/
    /** ****/ 	// The require function
    /** ****/ 	function __webpack_require__(moduleId) {
      /** ****/ 		// Check if module is in cache
      /** ****/ 		const cachedModule = __webpack_module_cache__[moduleId];
      /** ****/ 		if (cachedModule !== undefined) {
        /** ****/ 			return cachedModule.exports;
        /** ****/ 		}
      /** ****/ 		// Create a new module (and put it into the cache)
      /** ****/ 		const module = __webpack_module_cache__[moduleId] = {
        /** ****/ 			id: moduleId,
        /** ****/ 			// no module.loaded needed
        /** ****/ 			exports: {},
        /** ****/ 		};
      /** ****/
      /** ****/ 		// Execute the module function
      /** ****/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
      /** ****/
      /** ****/ 		// Return the exports of the module
      /** ****/ 		return module.exports;
      /** ****/ 	}
    /** ****/
    /** **********************************************************************/
    /** ****/ 	/* webpack/runtime/compat get default export */
    /** ****/ 	!(function () {
      /** ****/ 		// getDefaultExport function for compatibility with non-harmony modules
      /** ****/ 		__webpack_require__.n = function (module) {
        /** ****/ 			const getter = module && module.__esModule
        /** ****/ 				? function () {
            return module.default;
          }
        /** ****/ 				: function () {
            return module;
          };
        /** ****/ 			__webpack_require__.d(getter, { a: getter });
        /** ****/ 			return getter;
        /** ****/ 		};
      /** ****/ 	}());
    /** ****/
    /** ****/ 	/* webpack/runtime/define property getters */
    /** ****/ 	!(function () {
      /** ****/ 		// define getter functions for harmony exports
      /** ****/ 		__webpack_require__.d = function (exports, definition) {
        /** ****/ 			for (const key in definition) {
          /** ****/ 				if (__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
            /** ****/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
            /** ****/ 				}
          /** ****/ 			}
        /** ****/ 		};
      /** ****/ 	}());
    /** ****/
    /** ****/ 	/* webpack/runtime/global */
    /** ****/ 	!(function () {
      /** ****/ 		__webpack_require__.g = (function () {
        /** ****/ 			if (typeof globalThis === 'object') return globalThis;
        /** ****/ 			try {
          /** ****/ 				return this || new Function('return this')();
          /** ****/ 			} catch (e) {
          /** ****/ 				if (typeof window === 'object') return window;
          /** ****/ 			}
        /** ****/ 		}());
      /** ****/ 	}());
    /** ****/
    /** ****/ 	/* webpack/runtime/hasOwnProperty shorthand */
    /** ****/ 	!(function () {
      /** ****/ 		__webpack_require__.o = function (obj, prop) {
        return Object.prototype.hasOwnProperty.call(obj, prop);
      };
      /** ****/ 	}());
    /** ****/
    /** ****/ 	/* webpack/runtime/make namespace object */
    /** ****/ 	!(function () {
      /** ****/ 		// define __esModule on exports
      /** ****/ 		__webpack_require__.r = function (exports) {
        /** ****/ 			if (typeof Symbol !== 'undefined' && Symbol.toStringTag) {
          /** ****/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
          /** ****/ 			}
        /** ****/ 			Object.defineProperty(exports, '__esModule', { value: true });
        /** ****/ 		};
      /** ****/ 	}());
    /** ****/
    /** ****/ 	/* webpack/runtime/publicPath */
    /** ****/ 	!(function () {
      /** ****/ 		__webpack_require__.p = '/';
      /** ****/ 	}());
    /** ****/
    /** **********************************************************************/
    const __webpack_exports__ = {};
    // This entry need to be wrapped in an IIFE because it need to be in strict mode.
    !(function () {
      'use strict';
      // ESM COMPAT FLAG
      __webpack_require__.r(__webpack_exports__);

      // EXPORTS
      __webpack_require__.d(__webpack_exports__, {
        default() {
          return /* binding */ lib_entry;
        },
      });

      // EXTERNAL MODULE: ./src/controller/form.tsx
      const controller_form = __webpack_require__(5502);
      // EXTERNAL MODULE: ./src/core/events.ts
      const events = __webpack_require__(3660);
      // EXTERNAL MODULE: ./src/core/schema.ts
      const schema = __webpack_require__(8683);
      ;// CONCATENATED MODULE: ./src/index.ts


      /* harmony default export */ const src = (controller_form/* default */.Z);


      ;// CONCATENATED MODULE: ./node_modules/@blueking/cli-service-webpack/dist/lib/lib-entry.js
      // runtime file

      /* harmony default export */ var lib_entry = (src);


      // 基于 script src，懒加载相关资源
      if (typeof window !== 'undefined') {
        const { currentScript } = window.document;
        const src = currentScript && currentScript.src.match(/(.+\/)[^/]+\.js(\?.*)?$/);
        if (src) {
    __webpack_require__.p = src[1] // eslint-disable-line
        }
      }
    }());
    /** ****/ 	return __webpack_exports__;
    /** ****/ }())));
