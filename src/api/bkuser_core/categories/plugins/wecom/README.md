# 创建插件目录
本地创建插件 
对应的插件名称为 wecom
domian 根据实际需要设置
```bash
python manage.py create_pluggable_category --name 企业微信 --domain some-domain.com --plugin wecom
```
默认地，以上步骤会创建一个 key 为 `wecom` 的 `Setting` 绑定到该目录。


# DB 初始化
配置同步所需的corpId和Secret
category_id: step1创建的目录的ID
settingmeta_wecom_corpid_id: settingmeta 表中key为wecom_corpid 的ID
settingmeta_wecom_secret_id: settingmeta 表中key为wecom_secret 的ID
```bash
insert into user_settings_setting(create_time,update_time,value,enabled,category_id,meta_id) values(now(),now(),"",0,{category_id},${settingmeta_wecom_corpid_id});
insert into user_settings_setting(create_time,update_time,value,enabled,category_id,meta_id) values(now(),now(),"",0,{category_id},${settingmeta_wecom_secret_id});
```

# 其他
企业微信接口频率限制
https://work.weixin.qq.com/api/doc/90000/90139/90312