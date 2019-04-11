"""
   UserTalkNetwork.py

   Descp: Implementation of User-Talk Pages

   Created on: 16/03/2019

   Copyright 2019 Youssef 'FRYoussef' El Faqir el Rhazoui <f.r.youssef@hotmail.com>
"""

import pandas as pd
import re

from .BaseNetwork import BaseNetwork
from ...data_controller import get_bot_names

class UserTalkNetwork(BaseNetwork):
    """
    This class use user-talk pages to perform a network,
    where NODES are wiki users who edit in a user-talk page, and a tie
    is inferred when user A edits the B's user-talk-page.
    Thus the EDGES are directed.

    Arguments:
        - Node:
            * own_u_edits: the number of edits in itself's user-talk-page
            * article_edits: edits in article pages
            * talk_edits: edits in talk pages
            * id: The user id in the wiki
            * label: the user name in the wiki

        - Edge:
            * id: sourceId + targetId
            * source: user_id
            * target: user_id
            * weight: the number of editions in the user-talk-page
    """

    NAME = 'User Talk Pages'
    CODE = 'user_talk_network'
    DIRECTED = True

    AVAILABLE_METRICS = BaseNetwork.AVAILABLE_METRICS.copy()
    AVAILABLE_METRICS['Edits in its own page'] = 'own_u_edits'
    AVAILABLE_METRICS['Edited user talks'] = 'user_talks'

    NODE_METRICS_TO_PLOT = BaseNetwork.NODE_METRICS_TO_PLOT.copy()
    NODE_METRICS_TO_PLOT['Edits in its own page'] = \
        {
            'key': 'own_u_edits',
            'max': 'max_own_u_edits',
            'min': 'min_own_u_edits'
        }
    NODE_METRICS_TO_PLOT['User Talks'] = \
        {
            'key': 'user_talks',
            'max': 'max_user_talks',
            'min': 'min_user_talks'
        }

    USER_INFO = {
        #'User ID': 'id',
        'Birth': 'birth',
        'Cluster #': 'cluster'
    }

    NODE_NAME = {
        'User': 'label'
    }


    def __init__(self, is_directed = True, graph = {}, alias = ''):
        super().__init__(is_directed, graph, alias)


    def generate_from_pandas(self, df):
        user_per_page = {}
        mapper_v = {}
        count_v = 0
        count_e = 0

        bots_name = get_bot_names(self.alias)
        dff = self.remove_non_user_talk_data(df)

        for _, r in dff.iterrows():
            ################ Filter ################
            # remove "User Page:"
            page_t = re.sub('^.+:', '', r['page_title'])
            # remove everyhing after slash
            page_t = re.sub('[\/].*', '', page_t)
            # filter anonymous user talk page for ipv4 or ipv6 (i.e it contains "." or ":")
            if re.search('\.|\:', page_t):
                continue
            # filter bots pages
            if page_t in bots_name:
                continue
            ########################################

            # Nodes
            if not r['contributor_name'] in mapper_v:
                self.graph.add_vertex(count_v)
                mapper_v[r['contributor_name']] = count_v
                self.graph.vs[count_v]['id'] = int(r['contributor_id'])
                self.graph.vs[count_v]['label'] = r['contributor_name']
                self.graph.vs[count_v]['own_u_edits'] = 0
                self.graph.vs[count_v]['user_talks'] = {int(r['page_id'])}
                count_v += 1

            # count diferent pages
            self.graph.vs[mapper_v[r['contributor_name']]]['user_talks'].add(int(r['page_id']))

            if page_t == r['contributor_name']:
                self.graph.vs[mapper_v[page_t]]['own_u_edits'] += 1
            else:
                # A page gets serveral contributors
                if not page_t in user_per_page:
                    user_per_page[page_t] = {r['contributor_name']: 1}
                else:
                    if r['contributor_name'] in user_per_page[page_t]:
                        user_per_page[page_t][r['contributor_name']] += 1
                    else:
                        user_per_page[page_t][r['contributor_name']] = 1

        # Edges
        if self.graph.vcount():
            max_id = max(self.graph.vs['id']) + 1
        else:
            max_id = 1

        for page_name, p_dict in user_per_page.items():
            for user, edits in p_dict.items():
                # it could be that an user has no edits but someone edits in its user-talk
                if page_name not in mapper_v:
                    self.graph.add_vertex(count_v)
                    mapper_v[page_name] = count_v
                    self.graph.vs[count_v]['id'] = max_id
                    max_id += 1
                    self.graph.vs[count_v]['label'] = page_name
                    self.graph.vs[count_v]['own_u_edits'] = 0
                    self.graph.vs[count_v]['user_talks'] = set()
                    count_v += 1

                self.graph.add_edge(mapper_v[user], mapper_v[page_name])
                source = self.graph.vs[mapper_v[user]]['id']
                target = self.graph.vs[mapper_v[page_name]]['id']
                edge_id = (source << 32) + target
                self.graph.es[count_e]['id'] = edge_id
                self.graph.es[count_e]['weight'] = edits
                self.graph.es[count_e]['source'] = source
                self.graph.es[count_e]['target'] = target
                count_e += 1

        # total pages
        if 'user_talks' in self.graph.vs.attributes():
            user_talks = [len(node['user_talks']) for node in self.graph.vs]
            self.graph.vs['user_talks'] = user_talks


    def get_metric_dataframe(self, metric):
        if self.AVAILABLE_METRICS[metric] in self.graph.vs.attributes()\
            and 'label' in self.graph.vs.attributes():

            df = pd.DataFrame({
                    'User': self.graph.vs['label'],
                    metric: self.graph.vs[self.AVAILABLE_METRICS[metric]]
                    })
            return df

        return pd.DataFrame()


    def add_others(self, df):
        self.calculate_edits(df, 'article')
        self.calculate_edits(df, 'talk')


    @classmethod
    def get_metric_header(cls, metric: str) -> list:
        header = list()
        if metric in cls.AVAILABLE_METRICS:
            header = [{'name': 'User', 'id': 'User'}, 
                {'name': metric, 'id': metric}]

        return header


    @classmethod
    def get_user_info(cls) -> dict:
        return cls.USER_INFO


    @classmethod
    def get_node_name(cls) -> dict:
        return cls.NODE_NAME


    @classmethod
    def is_directed(cls):
        return cls.DIRECTED


    @classmethod
    def get_network_description(cls) -> dict:
        desc = {}
        desc['min_node_color'] = 'Lowest value in selected metric'
        desc['max_node_color'] = 'Highest value in selected metric'
        desc['min_node_size'] = 'Low edits in its own page'
        desc['max_node_size'] = 'High edits in its own page'
        desc['min_edge_size'] = 'A weak friendship'
        desc['max_edge_size'] = 'A strong friendship'
        return desc


    @classmethod
    def get_main_class_metric(cls) -> str:
        if 'Edits in its own page' in cls.NODE_METRICS_TO_PLOT:
            return cls.NODE_METRICS_TO_PLOT['Edits in its own page']
        else:
            return ''


    @classmethod
    def get_main_class_key(cls) -> str:
        metric = cls.get_main_class_metric()
        return metric['key'] if metric and 'key' in metric else ''