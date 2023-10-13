import asyncio
import functools
import aioconsole
import subprocess

import time



coada = asyncio.Queue()
class ClientEcho(asyncio.Protocol):
    def __init__(self, future, username):

        self.bucla = future
        self.username = username
        self.choosing_receiver = 0
        self.accept_being_receiver = 0

    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        print('Conexiunea acceptata cu _{}_{}'.format(*self.address))
        transport.write(bytes("username: " + self.username, 'utf-8'))

        print("Am trimis username-ul")



        asyncio.ensure_future(self.send())
        asyncio.ensure_future(self.just_write())


        # while(True):
        #     time.sleep(2)

    def data_received(self, data):
        print("{}\n".format(data.decode()))
        if(data.decode().__contains__("Doresti sa vorbesti cu cineva in particular sau vorbesti pe chat-ul global?")):
           self.choosing_receiver = 1

        if(data.decode().__contains__("vrea sa vorbeasca cu tine. Accepti?\n1.Da\t2.Nu")):
            self.accept_being_receiver = 1
            self.sender = data.decode().split("vrea")[0]







    def eof_received(self):
        print("eof received")
        self.transport.close()
        if not self.bucla.done():
            self.bucla.set_result(True)

    def connection_lost(self, error):
        self.transport.close()
        if not self.bucla.done():
            self.bucla.set_result(True)
        super().connection_lost(error)


    async def choose(self):
        print("Cu cine vrei sa vorbesti?")

    async def send(self):

        while(True):
            if not coada.empty():
                mesaj = await coada.get()
                if(self.choosing_receiver == 1):
                    self.transport.write(bytes("Doresc sa vorbesc cu: " + mesaj, 'utf-8'))
                    self.choosing_receiver = 0
                elif (self.accept_being_receiver == 1):
                    self.transport.write(bytes(self.sender + " Alegerea mea sa vorbesc cu el este: " + mesaj, 'utf-8'))
                    self.accept_being_receiver = 0
                else:
                    self.transport.write(bytes(mesaj, 'utf-8'))
            await asyncio.sleep(2)

    async def just_write(self):
        while (True):
            mesaj = await aioconsole.ainput()
            await coada.put(mesaj)
            await asyncio.sleep(2)


    async def menu(self):
        print("Ce iti doresti sa faci")



        # self.transport.close()






if __name__ == '__main__':

    my_event_loop = asyncio.get_event_loop()

    print('Salut! Pentru inceput, am nevoie de un username: ')
    username = input('Introdu un username\n')

    print('Bine ai venit! ' + username)

    x = int (input('Incepem? 1. Da  2. Nu\n'))
    if(x == 1):
        try:
            client_completed = asyncio.Future()


            client_factory = functools.partial(ClientEcho, future=client_completed, username=username,)

            factory_coroutine = my_event_loop.create_connection(client_factory, 'localhost', 10000)

            my_event_loop.run_until_complete(factory_coroutine)

            my_event_loop.run_forever()

        except:
            print("Se pare ca nu am reusit sa fac conexiunea, imi pare foarte rau!")
        finally:
            print('ok')
    else:
        print('Ok, lasam pe alta data')
        exit(0)
