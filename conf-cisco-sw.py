#!/usr/bin/python3
#-*- coding: utf-8-*-

import serial
from time import sleep

####
# Este script fará a configuração inicial de um switch Cisco. Os comandos de execução estão ao final deste arquivo (linha 246).
# Para a sua execução é necessário o módulo pyserial, a instalação pode ser feita com:
# sudo pip3 install pyserial
# Após a configuração dos métodos ao final do arquivo, basta executar:
# python3 script.py
####


class Switch():
    
    ####
    # Método responsável por fazer a conexão e gerar um objeto de console (onde será possível executar os comandos no switch)
    # Este método deve receber a porta de conexão, por exemplo: COM1, COM2, COM3...
    ####

    def __init__(self, port):
        try:
            self.console = serial.Serial(port=port,
                                    baudrate=9600,
                                    parity="N",
                                    stopbits=1,
                                    bytesize=8,
                                    timeout=8)
            self.console.flushInput()
            print ("Conexão feita com sucesso... \nIniciando configuracao...")

        except Exception as e:
            print("Erro ao conectar: %s" %e)
			

    ####
    # Método responsável por sair do menu de "auto-configuração" inicial do cisco. Ele deve ser chamado antes da configuração do switch.
    # Exemplo: conf_inicial()
    ####

    def conf_inicial(self):
        self.console.write(bytes("\r\n", 'utf-8'))
        self.console.write(bytes("no \r\n", 'utf-8'))
        self.console.write(bytes("yes \r\n", 'utf-8'))
        


    ####
    # Método que irá entrar no modo de configuração do switch. Ele deve ser chamado por outros métodos que necessitem estar dentro do modo de configuração (configure terminal).
    ####

    def config_terminal(self):
        self.console.write(bytes("end \r\n", 'utf-8'))
        self.console.write(bytes("enable \r\n", 'utf-8'))
        self.console.write(bytes("conf t \r\n", 'utf-8'))

    ####
    # Método que irá configurar o hostname e horário do switch, ele deverá receber o hostname. 
    # Caso seja executado com sucesso, ele irá retornar na tela uma mensagem com esta informação.
    ####

    def hostname(self, name):
        try:
            print ("Configurando hostname")
            self.config_terminal()
            self.console.write(bytes("hostname %s \r\n" %name, 'utf-8'))
            self.console.write(bytes("clock timezone GMT -3 \r\n", 'utf-8'))        
            print ("Hostname alterado para %s com sucesso!" %name)
        except Exception as e:
            print("Erro ao configurar hostname: %s" %e)


    ####
    # Método que fará a configuração SSH, para isto ele deve receber o usuário(str) e a senha(str).
    # Caso seja executado com sucesso, ele irá retornar na tela uma mensagem com esta informação.
    # Exemplo: login_ssh("usuario","senha")
    ####

    def login_ssh(self, user, password):
        try:
            print ("Configurando SSH")            
            self.config_terminal()
            self.console.write(bytes("username %s privilege 15 secret %s \r\n" %(user, password), "utf-8"))
            self.console.write(bytes("line vty 0 4 \r\n", "utf-8"))
            self.console.write(bytes("transport input ssh \r\n", "utf-8"))
            self.console.write(bytes("login local \r\n", "utf-8"))
            print("SSH configurado com sucesso, usuario: %s senha: %s" %(user, password))
        except Exception as e:
            print("Erro ao configurar ssh: %s" %e)

    ####
    # Método que irá adicionar o IP na interface VLAN, ele deve receber qual é a interface (str), o IP (str) e a MASK (str).
    # Exemplo: add_ip_vlan("10","192.168.0.1","255.255.255.0")
    ####

    def add_ip_vlan(self, interface, ip, mask):
        try:
            print ("Adicionando IP na VLAN")
            self.config_terminal()
            self.console.write(bytes("interface vlan %s \r\n" %interface, "utf-8"))
            self.console.write(bytes("ip address %s %s \r\n" %(ip, mask), "utf-8"))
            print("IP %s adicionado na interface %s com sucesso" %(ip, interface))
        except Exception as e:
            print("Erro ao configurar ip: %s" %e)

    ####
    # Método para adicionar VLAN, deve receber o número(str) e o nome(str).
    # Exemplo: add_vlan("40", "nome_vlan")
    ####
    
    def add_vlan(self, number, name):
        try:
            print ("Adicionando VLAN")
            self.config_terminal()
            self.console.write(bytes("vlan %s \r\n" %number, "utf-8"))

            self.console.write(bytes("name %s \r\n" %name, "utf-8"))
            print ("Vlan %s adicionada com sucesso!" %name)
        except Exception as e:
            print("Erro ao adicionar vlan: %s" %e)

    ####
    # Método para definir uma ou mais interfaces para mode trunk. Ele deve receber o número da interface(str) e range(bool), caso queira configurar o range.
    # Exemplo de uma interface: interface_trunk("1/0/1")
    # Exemplo de um range: interface_trunk("1/0/1-48",range=True)
    ####

    def interface_trunk(self, interface, range=False):
        try:
            print ("Alterando interface para trunk")
            self.config_terminal()
            if range:
                self.console.write(bytes("interface range GigabitEthernet %s \r\n" %interface, "utf-8"))
            else:
                self.console.write(bytes("interface GigabitEthernet %s \r\n" %interface, "utf-8"))
            self.console.write(bytes("switchport mode trunk \r\n", "utf-8"))
            print("A interface %s foi alterada para trunk" %interface)
        except Exception as e:
            print("Erro ao configurar interface trunk: %s" %e)


    ####
    # Método para definir uma ou mais interfaces para mode access. Ele deve receber o número da interface(str), o numero da vlan (str) e range(bool), caso queira configurar o range.
    # Exemplo de uma interface: interface_trunk("1/0/1", "10")
    # Exemplo de um range: interface_trunk("1/0/1-48","10", range=True)
    ####
    
    def interface_access(self, interface, vlan, range=False):
        try:
            print ("Alterando interface para access")
            self.config_terminal()
            if range:
                self.console.write(bytes("interface range GigabitEthernet %s \r\n" %interface, "utf-8"))
            else:
                self.console.write(bytes("interface GigabitEthernet %s \r\n" %interface, "utf-8"))
            self.console.write(bytes("switchport access vlan %s \r\n" %vlan, "utf-8"))
            self.console.write(bytes("switchport mode access \r\n", "utf-8"))
            print("A interface %s foi alterada para trunk" %interface)
        except Exception as e:
            print("Erro ao configurar interface access: %s" %e)


    ####
    # Método para configurar a rota padrão, ele deve receber o IP do gatweay (str).
    # Exemplo: default_route("192.168.10.1")
    ####

    def default_route(self, ip):
        try:
            print("Configurando rota default")
            self.config_terminal()
            self.console.write(bytes("ip route 0.0.0.0 0.0.0.0 %s \r\n" %ip, "utf-8"))
            self.console.write(bytes("ip forward-protocol nd \r\n", "utf-8"))
            print ("Rota default configurada: %s" %ip)
        except Exception as e:
            print("Erro ao configurar rota default: %s" %e)


    ####
    # Método para configurar o servidor HTTP.
    # Exemplo: server_http()
    ####

    def server_http(self):
        try:
            print ("Configurando servidor HTTP")
            self.config_terminal()
            self.console.write(bytes("ip http server \r\n", "utf-8"))
            self.console.write(bytes("ip http authentication local \r\n", "utf-8"))
            self.console.write(bytes("http secure-server \r\n", "utf-8"))
            print("Servidor HTTP configurado")
        except Exception as e:
            print("Erro ao configurar rota default: %s" %e)


    ####
    # Método para configurar o Channel Group em uma interface, ele deve receber o número da interface(str).
    # Exemplo: channel_group("1/0/1")
    ####

    def channel_group(self, interface):
        try:
            print("Configurando Channel Group")
            self.config_terminal()
            self.console.write(bytes("interface GigabitEthernet %s \r\n" %interface, "utf-8"))
            self.console.write(bytes("channel-group 2 mode on \r\n", "utf-8"))
            print ("Channel Group configurado na interface %s" %interface)
        except Exception as e:
            print("Erro ao configurar channel-group: %s" %e)


    ####
    # Método para configurar o Port-Channel em uma interface, ele deve receber o número da vlan(str).
    # Exemplo: port_channel("10")
    ####

    def port_channel(self, vlan):
        try:
            print("Configurando Port-channel")
            self.config_terminal()
            self.console.write(bytes("interface Port-channel 2 \r\n", "utf-8"))
            self.console.write(bytes("switchport access vlan %s \r\n" %vlan, "utf-8"))
            print ("Port-channel configurado na VLAN %s" %vlan)
        except Exception as e:
            print("Erro ao configurar port-channel: %s" %e)


    ####
    # Método para gravar as configurações do switch, ele deve ser chamado ao final da configuração.
    # Exemplo: save()
    ####
    
    def save(self):
        try:
            print ("Salvando as configuracoes")
            self.config_terminal()
            self.console.write(bytes("write memory \r\n", "utf-8"))
            print ("Configuracoes salvas!")
        except Exception as e:
            print("Erro ao salvar as configuracoes: %s" %e)


if __name__ == '__main__':
    # cria conexão com o switch, substituir PORT pela conexão (exemplo: COM3)
    switch = Switch("PORT")

    # faz a configuração inicial do swtich
    switch.conf_inicial()
    sleep(3)

    # configura o hostname, substituir o HOSTNAME pelo host que irá utilizar
    switch.hostname("HOSTNAME")
    sleep(3)
    
    # configurar SSH, substitua USER pelo usuário e PASSWORD pela senha
    switch.login_ssh("USER","PASSWORD")
    sleep(3)
    
    # adicionar VLAN, substitua 10 pelo número da VLAN e NAME pelo nome.
    switch.add_vlan("10","NAME")
    sleep(3)

    # adicionar IP na VLAN, substitua 10 pelo numero da vlan, 192.168.0.1 pelo IP e 255.255.255.0 pela mascara.
    switch.add_ip_vlan("10", "192.168.0.1", "255.255.255.0")
    sleep(3)


    # coloca a porta em mode trunk, substitua 1/0/1 pela porta em que deseja colocar.
    switch.interface_trunk("1/0/1")
    sleep(3)

    # coloca porta em modo access, substitua 1/0/1 pela porta em que deseja colocar e 10 pelo número da vlan que terá acesso a porta.
    switch.interface_access("1/0/1", "10")

    # coloca um range de portas em mode access, substitua 1/0/1-48 pela portas que quer configurar onde 1/0/1-20 (1=primeira 20=ultima), substitua 10 pelo numero da VLAN
    # e informe que a configuracao sera de um range com a opcao range=True
    switch.interface_access("1/0/1-48", "10", range=True)

    # adiciona uma rota default, substitua 192.168.0.1 pelo IP do gateway
    switch.default_route("192.168.0.1")
    sleep(3)

    # habilita e configura o servidor HTTP
    switch.server_http()
    sleep(3)

    # habilita channel group, substituia 1/0/1 pela porta que deseja habilitar
    switch.channel_group("1/0/1")
    sleep(3)

    # configura port channel, substitua o 10 pela vlan que deseja configurar
    switch.port_channel("10")
    sleep(3)

    # gravar as configuraçoes feitas
    switch.save()

    input("Configuracao finalizada, aperte enter para sair \n")
    exit()

####
# Caso seja necessário colocar mais de uma VLAN ou configurar mais de uma interface basta copiar as linhas e colar abaixo.
# É necessário sempre colocar sleep(3) ao final de cada tarefa executada pois
# desta forma os comandos tem tempo para executar e não se sobreescrevem uma vez que 
# os métodos executam sempre mais de um comando.
####
