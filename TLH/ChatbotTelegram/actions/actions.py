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
from rasa_sdk.events import FollowupAction

from .helper import DataHandler
import re

DATA=DataHandler()
def check_supermarket() :
    if DATA.supermarket is None:
        return False
    return True


class ActionPreguntarSupermercado(Action):
    def name(self) -> Text:
        return "action_preguntar_supermercado"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        supermarkets = DATA.get_supermarkets()
        dispatcher.utter_message(text=f"Tengo productos de los supermercados: {', '.join(supermarkets)}")
        return []
    
class ActionSetSupermercado(Action):
    def name(self) -> Text:
        return "action_set_supermercado"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        supermarket = tracker.latest_message.get("text").lower()
        if DATA.set_supermarket(supermarket):
            dispatcher.utter_message(text=f"¡Perfecto! Estamos comprando en {DATA.supermarket}")
        else:
            dispatcher.utter_message(text=f"¡Ups! No tengo información del supermercado {DATA.supermarket}")
        return []
    
class ActionSugerirProducto(Action):
    def name(self) -> Text:
        return "action_sugerir_producto"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if not check_supermarket():
            dispatcher.utter_message(text="¡Ups! No se en que supermercado estas comprando")
            return [FollowupAction("action_preguntar_supermercado")]
        
        producto = DATA.get_random_product()
        dispatcher.utter_message(text=f"Te recomiendo {producto['name']} que cuesta {producto['price']}€")
        return []
    
class ActionSugerirPorPrecio(Action):
    def name(self) -> Text:
        return "action_sugerir_por_precio"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if not check_supermarket():
            dispatcher.utter_message(text="¡Ups! No se en que supermercado estas comprando")
            return [FollowupAction("action_preguntar_supermercado")]
        
        precio = tracker.latest_message.get("text")
        precio = re.findall(r"\d+", precio)

        if not precio:
            dispatcher.utter_message(text="No he entendido el precio")
            return []
        
        productos = DATA.get_by_price(float(precio[0]))
        if not productos:
            dispatcher.utter_message(text=f"¡Ups! No tengo productos por debajo de {precio}€")
        else:
            # Seleccionamos 5 productos mas cercanos a el precio
            dispatcher.utter_message(text=f"Los prodictos que te recomiendo son:")
            for p in productos[:5]:
                dispatcher.utter_message(text=f"{p['name']} cuesta {p['price']}€")
        return []
    
class ActionSugerirPorCategoria(Action):
    def name(self) -> Text:
        return "action_sugerir_por_categoria"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if not check_supermarket():
            dispatcher.utter_message(text="¡Ups! No se en que supermercado estas comprando")
            return [FollowupAction("action_preguntar_supermercado")]
        
        categoria = tracker.latest_message.get("entities", [])
        categoria = [e["value"] for e in categoria if e["entity"] == "categoria"]
        if not categoria:
            dispatcher.utter_message(text="No he entendido la categoría")
            return []
        productos = DATA.get_by_category(categoria[0].lower())
        if not productos:
            dispatcher.utter_message(text=f"¡Ups! No tengo productos de la categoría {categoria}")
        else:
            dispatcher.utter_message(text=f"Los mejores productos de la categoría {categoria} son:")

            for i in range (5):
                p = productos[i]
                dispatcher.utter_message(text=f"{p['name']} cuesta {p['price']}€")
        return []

class ActionBuscarCategoria(Action):
    def name(self) -> Text:
        return "action_buscar_categoria"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if not check_supermarket():
            dispatcher.utter_message(text="¡Ups! No se en que supermercado estas comprando")
            return [FollowupAction("action_preguntar_supermercado")]
        
        entities = tracker.latest_message.get("entities", [])
        categorias = [e["value"] for e in entities if e["entity"] == "categoria"]
        if not categorias:
            dispatcher.utter_message(text=f"No he entendido la categoría en la que quieres buscar")
            return []
        for categoria in categorias:
            p = DATA.get_by_category(categoria)
            if not p:
                categorias_similares = DATA.get_similar(categoria, type="category")
                dispatcher.utter_message(text=f"¡Ups! No tengo la categoría {categoria}. ¿Te refieres a {', '.join(categorias_similares)}?")
        return []

class ActionGetCategorias(Action):
    def name(self) -> Text:
        return "action_get_categorias"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if not check_supermarket():
            dispatcher.utter_message(text="¡Ups! No se en que supermercado estas comprando")
            return [FollowupAction("action_preguntar_supermercado")]
        
        categorias = DATA.get_categories()[:5]
        dispatcher.utter_message(text=f"Las categorías que tengo son: {', '.join(categorias)}")
        return []
    
class ActionBuscarProducto(Action):
    def name(self) -> Text:
        return "action_buscar_producto"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if not check_supermarket():
            dispatcher.utter_message(text="¡Ups! No se en que supermercado estas comprando")
            return [FollowupAction("action_preguntar_supermercado")]
        
        entities = tracker.latest_message.get("entities", [])
        productos = [e["value"] for e in entities if e["entity"] == "producto"]
        if not productos:
            dispatcher.utter_message(text="No he entendido que producto quieres buscar")
            return []
        for producto in productos:
            p = DATA.get_by_name(producto)
            if not p:
                productos_similares = DATA.get_similar(producto)
                dispatcher.utter_message(text=f"¿Algunos similares son:")
                for ps in productos_similares:
                    dispatcher.utter_message(text=f"{ps}")
            else:
                dispatcher.utter_message(text=f"¡Claro! {p[0]['name']} cuesta {p[0]['price']}€")
        return []

class ActionIncluirProducto(Action):
    def name(self) -> Text:
        return "action_incluir_producto"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if not check_supermarket():
            dispatcher.utter_message(text="¡Ups! No se en que supermercado estas comprando")
            return [FollowupAction("action_preguntar_supermercado")]
        
        entities = tracker.latest_message.get("entities", [])
        nuevos_productos = [e["value"] for e in entities if e["entity"] == "producto"]
        lista = tracker.get_slot("lista_compra") 
        if nuevos_productos:
            producto = nuevos_productos[0]
        if not nuevos_productos or not DATA.get_by_name(producto):
            producto = tracker.latest_message.get("text")
        if producto:
            p = DATA.get_by_name(producto)
            if not p:
                dispatcher.utter_message(text=f"¡Ups! No tengo {producto} en el supermercado {DATA.supermarket}")
                return [FollowupAction("action_buscar_producto")]
            elif p[0]["name"] in lista:
                dispatcher.utter_message(text=f"¡Ups! {producto} ya está en la lista de ingredientes")
            else:
                lista.append(p[0]["name"])
                dispatcher.utter_message(text=f"¡Claro! Añado {p[0]['name']} a la lista de ingredientes")
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

        if not productos_a_eliminar:
            dispatcher.utter_message(text="No he entendido que ingrediente quieres eliminar")
            return [SlotSet("lista_compra", lista)]
        
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
            DATA.supermarket = None
        
        return [SlotSet("lista_compra", [])]