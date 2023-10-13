import asyncio
import subprocess

'''
#transport determines how bytes are transmitted
#protocol determines which bytes to transmit (si uneori cand se transmit)
#un transport este o abstractizare a unui socket
#cele doua combinatii ofera de fapt o interfata pentru utilizarea unui network si interproceselor

#transports sunt clase puse la dispozitie de asyncio pentru a abstractiza diferite variatii de canale de comunicare
# !nu sunt thread safe!

Atentie, se creeaza o instanta asyncio Protocol pentru fiecare client
'''

my_clients = {}
my_usernames = {}
options_for_each_client = {}


class ServerEcou(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        print("M am initializat ? ? ? ? ? ?? ")


    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')





        print('Conexiunea acceptata cu _{}_{}'.format(*self.address))
        print("Acum clientii mei sunt:")
        print(my_clients)
        print(my_usernames)
        self.optiune = 0



    #cand se trimit date de la client la server

    def data_received(self, data):
        print("Clientul cu care vrea sa vorbeasca este: " + str(self.optiune))
        mesaj = data.decode()
        print(mesaj)

        if mesaj.__contains__("username:"):
            print("Contine")
            nume = mesaj.split(": ")
            self.transport.write(b'Bine ai venit, ' + bytes(nume[1], 'utf-8') + b'!')

            if len(my_clients) == 0:
                self.transport.write(
                    b'Esti primul utilizator!')
            else:
                self.transport.write(b'Iata lista de persoane active: ' + bytes(str(my_usernames.values()), 'utf-8')  + b'!\n')
                self.transport.write(b'Doresti sa vorbesti cu cineva in particular sau vorbesti pe chat-ul global?')

            my_clients[self.address[1]] = self.transport
            my_usernames[self.address[1]] = nume[1]
            options_for_each_client[self.address[1]] = 0

            for key, value in my_clients.items():
                if key != self.address[1]:
                    value.write(b'Sa stii ca tocmai s-a conectat si: ' + data)

        elif mesaj.__contains__("Doresc sa vorbesc cu: "):

            print("Acum incerc sa splituiesc optiunea " + mesaj)
            self.optiune = int(mesaj.split(": ")[1])
            options_for_each_client[self.address[1]] = self.optiune
            print("Clientul cu care vrea sa vorbeasca este: " + str(self.optiune))
            if(self.optiune != 0):
                see_available_options = list(options_for_each_client.values())
                print(see_available_options)
                if(see_available_options[self.optiune-1] == 0):
                    corespondent = list(my_clients.values())[self.optiune - 1]
                    corespondent.write(
                        bytes(my_usernames[self.address[1]], 'utf-8') + b' ' + bytes("vrea sa vorbeasca cu tine. Accepti?\n1.Da\t2.Nu", 'utf-8'))
                else:
                    self.transport.write(bytes("Este ocupat", 'utf-8'))
            else:
               self.transport.write(bytes("Ai ales chat-ul global.", 'utf-8'))


        elif mesaj.__contains__("Alegerea mea sa vorbesc cu el"):
            alegere = mesaj.split("este: ")[1]
            sender = mesaj.split("  Alegerea")[0]
            print("Acesta este senderul: " + sender + "!")

            print(my_usernames)
            print("Lista de adrese: ")

            lista_adrese = list(my_usernames.keys())
            lista_nume = list(my_usernames.values())

            print(lista_adrese)

            index_sender = lista_nume.index(sender)
            adresa_sender = lista_adrese[index_sender]


            print("Adresa la care trimit este: " + str(adresa_sender))
            print("Transportul este " + str(my_clients[adresa_sender]))
            if(int(alegere) == 2):
                my_clients[adresa_sender].write(bytes("Nu vrea sa vorbeasca cu tine. Nu v-ati conectat!", 'utf-8'))
                options_for_each_client[adresa_sender] = 0
            else:
                my_clients[adresa_sender].write(bytes("Vrea sa vorbeasca cu tine. V-ati conectat!", 'utf-8'))
                options_for_each_client[self.address[1]] = lista_nume.index(sender) + 1
                #options_for_each_client[self.address[1]] = list(my_clients.values()).index(self.address)

        elif (mesaj.__contains__("Leave conversation")):
            # de vazut
            options_for_each_client[self.address[1]] = 0

        else:
            print("Iata optiunile" + str(options_for_each_client))
            if(options_for_each_client[self.address[1]] == 0):
                print("Iata ce am primit " + mesaj + " de la  " + str(self.transport))
                for key, value in my_usernames.items():
                    if key != self.address[1]:
                      my_clients[key].write(bytes(my_usernames[self.address[1]], 'utf-8') + b': ' + bytes(mesaj, 'utf-8'))
            else:

                corespondent = list(my_clients.values())[ options_for_each_client[self.address[1]] - 1]

                corespondent.write(
                            bytes(my_usernames[self.address[1]], 'utf-8') + b': ' + bytes(mesaj, 'utf-8'))


    def eof_received(self):
        print("received EOF")
        if self.transport.can_write_eof():
            self.transport.write_eof()

    def connection_lost(self, error):
        print("Am inchis un socket " + str(self.address[1]))
        if error:
            print("Eroaare! " + str(error))
        else:
            print("Inchid socket")
        super().connection_lost(error)



my_event_loop = asyncio.get_event_loop()

factory = my_event_loop.create_server(ServerEcou, 'localhost', 10000)
server = my_event_loop.run_until_complete(factory)


try:
    my_event_loop.run_forever()
except:
    print('inchid server')
    server.close()
    my_event_loop.run_until_complete(server.wait_closed())
    print('inchide loop ul')
    my_event_loop.close()