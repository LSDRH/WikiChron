"""
   Stylesheet.py

   Descp: A class to implement the decorator pattern in order to make an
     easier implementation of networks stylesheet

   Created on: 30/01/2019

   Copyright 2019 Youssef 'FRYoussef' El Faqir el Rhazoui <f.r.youssef@hotmail.com>
"""
import abc

class Stylesheet(metaclass=abc.ABCMeta):


	def __init__(self, cy_stylesheet = []):
		if not cy_stylesheet:
			self.cy_stylesheet = self.make_basic_stylesheet()
		else:
			self.cy_stylesheet = cy_stylesheet

	def color_nodes(self, _):
		self.cy_stylesheet[0]['style']['background-color'] = '#0D47A1'


	def color_nodes_by_cluster(self):
		self.cy_stylesheet[0]['style']['background-color'] = 'data(cluster_color)'


	def size_nodes(self, _):
		self.cy_stylesheet[0]['style']['height'] = '30'
		self.cy_stylesheet[0]['style']['width'] = '30'
		self.size_font_labels()


	def size_font_labels(self, _):
		self.cy_stylesheet[0]['style']['font-size'] = '12'


	def color_edges(self, _):
		self.cy_stylesheet[1]['style']['line-color'] = '#000000'


	def set_edges_opacity(self, _):
		self.cy_stylesheet[1]['style']['opacity'] = '1'


	def size_edges(self, _):
		self.cy_stylesheet[1]['style']['width'] = '1'


	def set_label(self, text):
		self.cy_stylesheet[0]['style']['content'] = text


	def make_basic_stylesheet(self):
		return [{
                'selector': 'node',
                'style': {
                    'content': '',
                    'text-halign': 'center',
                    'text-valign': 'top',
                    'text-background-color': '#FFFFFF',
                    'text-background-opacity': '1',
                    'font-size': '12',
                    'background-color': '#0D47A1',
                    'height': '30',
                    'width': '30'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    "width": 1,
                    'opacity': '1',
                    'line-color': "#000000",
                }
            }]