# enterprise-infra-lab

Repositorio de infraestructura como código para el laboratorio. Contiene los playbooks de Ansible para el aprovisionamiento, configuración y operación de los servidores del entorno.

## Descripción

Gestiona el ciclo de vida completo de la aplicación Flask ([enterprise-app-lab](https://github.com/martirentani8902/enterprise-app-lab)) y la configuración de monitoreo con Zabbix Agent 2 sobre Debian.

## Estructura
```
enterprise-infra-lab/
├── ansible.cfg
├── inventory/
│   ├── lab.yml                     # Inventario del laboratorio
│   ├── group_vars/
│   │   └── all.yml                 # Variables globales
│   └── host_vars/                  # Variables por host (PSK de Zabbix, etc.)
│       ├── app01.lab.local.yml
│       ├── app02.lab.local.yml
│       ├── ci01.lab.local.yml
│       └── edge01.lab.local.yml
├── playbooks/
│   ├── bootstrap_flaskapp.yml      # Preparación inicial de servidores app
│   ├── deploy_flaskapp.yml         # Deploy de nueva versión
│   ├── rollback.yml                # Rollback a release anterior
│   ├── zabbix_agent2.yml           # Instalación de Zabbix Agent 2
│   ├── configurar_zabbix.yml       # Configuración PSK y template del agente
│   ├── reboot.yml                  # Reinicio de servidores
│   └── shutdown.yml                # Apagado de servidores
└── templates/
    ├── flaskapp.env.j2             # Variables de entorno de la app
    ├── flaskapp.service.j2         # Unit de systemd para la app
    └── zabbix_agent2.conf.j2       # Configuración del agente Zabbix
```

## Requisitos

- Ansible Core 2.x
- Acceso SSH con clave a los hosts del inventario
- Colección `community.general` (para módulo UFW)
```bash
ansible-galaxy collection install community.general
```

## Playbooks

### Bootstrap de servidores de aplicación

Prepara los servidores desde cero: instala dependencias, crea usuario y directorios, configura el servicio systemd y el virtualenv de Python.
```bash
ansible-playbook -i inventory/lab.yml playbooks/bootstrap_flaskapp.yml
```

### Deploy de la aplicación Flask

Clona el repositorio de la app, empaqueta un artefacto, lo distribuye a los servidores, instala dependencias y activa el nuevo release. Verifica el health check al final.
```bash
ansible-playbook -i inventory/lab.yml playbooks/deploy_flaskapp.yml
```

### Rollback

Apunta el symlink `current` a un release anterior identificado por su commit corto y reinicia el servicio.
```bash
ansible-playbook -i inventory/lab.yml playbooks/rollback.yml -e "rollback_id=<commit_short>"
```

### Instalación de Zabbix Agent 2

Instala Zabbix Agent 2 desde el repositorio oficial de Zabbix 7.0 en todos los hosts.
```bash
ansible-playbook -i inventory/lab.yml playbooks/zabbix_agent2.yml
```

### Configuración de Zabbix Agent 2

Despliega la clave PSK y el template de configuración del agente. La clave PSK se define por host en `host_vars/<hostname>.yml`.
```bash
ansible-playbook -i inventory/lab.yml playbooks/configurar_zabbix.yml
```

### Operaciones de servidores
```bash
# Reiniciar todos los servidores
ansible-playbook -i inventory/lab.yml playbooks/reboot.yml

# Apagar todos los servidores
ansible-playbook -i inventory/lab.yml playbooks/shutdown.yml

# Limitar a un host específico
ansible-playbook -i inventory/lab.yml playbooks/reboot.yml -l app01.lab.local
```

## Variables por host

Cada host tiene su archivo en `inventory/host_vars/`. Como mínimo debe contener la clave PSK para Zabbix:
```yaml
# inventory/host_vars/app01.lab.local.yml
zabbix_psk: "<clave_hex>"
```
