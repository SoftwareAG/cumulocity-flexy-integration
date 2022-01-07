# Mappings for accounts


|Data Field talk2M| Cumulocity fragment in tenant properties|
| ---------- | ---------- |
|`accountReference`|`"key": "talk2m.accountReference"`|
|`accountName`|`"key": "talk2m.accountName"`|
|`company`|`"key": "talk2m.company"`|
|`attribute1`|`"key": "talk2m.attribute1"`|
|`attribute2`|`"key": "talk2m.attribute2"`|
|`attribute3`|`"key": "talk2m.attribute3"`|
|`accountType`|`"key": "talk2m.accountType"`|
|`success`|`"key": "talk2m.success"`|

# Implementation Mapping Account

| key                                    | value 
----------------------------|-------------
 `talk2m.accountReference` |  `"eWON_sales"` 
​`talk2m.accountType`         | `"Pro"` 
 `talk2m.company`              | `"Ewon - HMS Industrial Networks S.A."` 
`talk2m.customAttributes`  | `"[LAN Devices,City,Country]"` 
​`talk2m.pools`                    | `"[{id:245189,name:Live Demo}]"` 
 `talk2m.success`                 | `"true"` 

# Mappings for devices
|Data Field talk2M| Cumulocity fragment in device|Display Name|
| ---------- | ---------- |---------- |
|`id`|externalID|External ID of type c8y_Serial|
|`name`|`"name":`|Name|
|`encodedName`|`talk2m.encodedName`| Encoded Name|
|`status`|to be discussed||
|`description`|`talk2m.description`| Description |
|`attribute1`|`talk2m.custom.attribute1"`| Attribute 1 |
|`attribute2`|`talk2m.custom.attribute2"`| Attribute 2 |
|`attribute3`|`talk2m.custom.attribute3"`| Attribute 3 |
|`m2webServer`|`talk2m.m2webServer"`| m2webServer |
|`ewonServices.name`|`talk2m.ewonServices.name"`| ewonServices Name|
|`ewonServices.description`|`talk2m.ewonServices.description"`| ewonServices Description|
|`ewonServices.port`|`talk2m.ewonServices.port"`| ewonServices Port|
|`ewonServices.protocol`|`talk2m.ewonServices.protocol"`| ewonServices Protocol |


# Implementation Mapping Device
```json
"talk2m": {
        "encodedName": "Machine+11",
        "lanDevices": [
            {
                "protocol": "http",
                "port": 80,
                "ip": "192.168.140.9",
                "name": "2. Camera",
                "description": ""
            },
            {
                "protocol": "http",
                "port": 80,
                "ip": "192.168.140.105",
                "name": "1. Click here for Demo Overview",
                "description": ""
            }
        ],
        "description": "Siemens Machine #2",
        "m2webServer": "eu1.m2web.talk2m.com",
        "ewonServices": [
            {
                "protocol": "http",
                "port": 81,
                "name": "Secondary HTTP Server",
                "description": "Secondary eWON Web Interface"
            },
            {
                "protocol": "http",
                "port": 80,
                "name": "HTTP Server",
                "description": "eWON Web Interface"
            }
        ],
        "customAttributes": [
            "Siemens S7-300 CPU312C PLC, IP Camera",
            "Charleroi",
            "Belgium"
        ]
    }
```


# Mappings for Measurements

|Data Field DataMailbox| Cumulocity fragment in device|Display Name|
| ---------- | ---------- |---------- |
|`id`|`externalId`|`EWON id`|
|`name`|`name`|`device name`|
|`tags.id`|`talk2m.tagId`|`Tag id`|
|`tags.name`|`measurementType`|`Measurement Type`|
|`tags.dataType`|`talk2m.dataType`|`Tag data type`|
|`tags.description`|`talk2m.description`|`Description`|
|`tags.alarmHint`|`needs to be mapped as an alarm`|`-----`|
|`tags.value`|`----`|`----`|
|`tags.quality`|`talk2m.quality`|`Quality`|
|`tags.ewonTagId`|`talk2m.ewonTagId`|`EWON Tag Id`|
|`tags.history.value`|`measurements.type.series.value`|`Value`|
|`tags.history.quality`|`TBD`|`TBD`|
