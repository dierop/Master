# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random
from rasa_sdk.events import SlotSet

class ActionSugiereIngredientes(Action):
    ingredientes = [
        "tomate",
        "cebolla",
        "pimiento",
        "aceitunas",
        "pepinillos",
        "atún",
        "huevo",
        "jamón",
        "jamón serrano",
        "queso",
        "mayonesa",
        "ketchup",
        "mostaza",
        "aceite",
        "vinagre",
        "sal",
    ]
    def name(self) -> Text:
        return "action_sugerir_ingrediente"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ingredientes_elegidos = random.sample(self.ingredientes, 1)
        dispatcher.utter_message(text=f"Te puede interesar añadir {ingredientes_elegidos[0]}")
        return []

class ActionIncluirIngrediente(Action):
    def name(self) -> Text:
        return "action_incluir_ingrediente"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get("entities", [])
        nuevos_productos = [e["value"] for e in entities if e["entity"] == "producto"]
        lista = tracker.get_slot("lista_compra") 
        
        if nuevos_productos:
            for producto in nuevos_productos:
                if producto in lista:
                    dispatcher.utter_message(text=f"¡Ups! {producto} ya está en la lista de ingredientes")
                else:
                    lista.append(producto)
                    dispatcher.utter_message(text=f"¡Claro! Añado {producto} a la lista de ingredientes")
            dispatcher.utter_message(text=f"Tu lista de ingredientes es: {', '.join(lista)}")
        else:
            dispatcher.utter_message(text="No he entendido que ingrediente quieres añadir")
        return [SlotSet("lista_compra", lista)]
    
class ActionEliminarIngrediente(Action):
    def name(self) -> Text:
        return "action_eliminar_ingrediente"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        entities = tracker.latest_message.get("entities", [])
        productos_a_eliminar = [e["value"] for e in entities if e["entity"] == "producto"]
        lista = tracker.get_slot("lista_compra")
        
        for producto in productos_a_eliminar:
            if producto in lista:
                lista.remove(producto)
                dispatcher.utter_message(text=f"¡Vale! Elimino {producto} de la lista de ingredientes")
            else:
                dispatcher.utter_message(text=f"¡Ups! No tengo {producto} en la lista de ingredientes")
        return [SlotSet("lista_compra", lista)]

    
class ActionHacerPedido(Action):
    def name(self) -> Text:
        return "action_hacer_pedido"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ingredientes = tracker.get_slot("lista_compra")
        
        if len(ingredientes) == 0:
            dispatcher.utter_message(text="No has añadido ningún ingrediente a la lista de la compra")
        else:
            dispatcher.utter_message(text=f"¡Perfecto! Tu pedido es: {', '.join(ingredientes)}")
        
        return [SlotSet("lista_compra", [])]