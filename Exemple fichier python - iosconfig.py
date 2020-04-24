#!/usr/bin/python
# -*- coding: utf-8 -*-
import jinja2

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'))

#instanciate template
template = template_env.get_template('iosconfig.conf')

config={}
config['hostname'] = 'CPE-ADMsp-SM1-01'
config['ntp'] = ['164.4.2.1','164.4.3.1']
config['tacacs'] = {'source_interface':'Loopback0','serveurs':['164.40.2.1','164.40.2.2'],'key':'cisco123'}
config['vrfs'] = {
                    1:{ 
                        'description':'Table de routage pour Environnement de PRODUCTION',
                        'name' : 'PRD',
                        'routes':[
                                   {'dest':'192.168.1.0/24','nexthop':'1.1.1.1','metric':'10','tag':'10'},
                                   {'dest':'192.168.2.0/24','nexthop':'2.2.2.2','metric':'10','tag':'11'},
                                 ]
                       },
                    
                    2:{   
                        'description':'Table de routage pour Environnement de RECETTE',
                        'name' : 'RQT',
                        'routes':[
                                    {'dest':'172.31.1.0/24','nexthop':'31.1.1.1','metric':'20','tag':'21'},
                                    {'dest':'172.31.2.0/24','nexthop':'31.2.2.2','metric':'20','tag':'22'},
                                  ]
                      }      

                  }



print(template.render(config))
