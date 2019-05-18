"""

 Author: Youssef El Faqir El Rhazoui
 Date: 13/Dec/2018
 Distributed under the terms of the GPLv3 license.

"""

import pandas as pd
from .BaseNetwork import BaseNetwork


class CoEditingNetwork(BaseNetwork):
    """
    This network is based on the editors cooperation, this means, the nodes
    are user from a wiki, and a edge will link two nodes if they edit the same
    page. As well, this network has the following args:

        - Node:
            * id: user id on the wiki
            * label: the user name with id contributor_id on the wiki
            * article_edits: the number of edit in the whole wiki
            * abs_birth: the first edit in the whole network

        - Edge:
            * source: contributor_id
            * target: contributor_id
            * weight: the number of cooperation in different pages on the wiki,
                      differents editions on the same page computes only once.

    """
    NAME = 'Co-Editing'
    CODE = 'co_editing_network'
    DIRECTED = False

    NETWORK_STATS = BaseNetwork.NETWORK_STATS.copy()
    NETWORK_STATS['Edited articles'] = 'wiki_articles'
    NETWORK_STATS['Article edits'] = 'wiki_article_edits'

    USER_INFO = {
        #'User ID': 'id',
        'Registered since': 'birth',
        'Cluster #': 'cluster',
    }

    NODE_NAME = {
        'Editor': 'label'
    }


    def __init__(self, is_directed = False, graph = {}, alias = ''):
        super().__init__(is_directed, graph, alias)


    def generate_from_pandas(self, df):
        user_per_page = {}
        mapper_v = {}
        mapper_e = {}
        count = 0
        dff = self.remove_non_article_data(df)

        for _, r in dff.iterrows():
            # Nodes
            if not int(r['contributor_id']) in mapper_v:
                self.graph.add_vertex(count)
                mapper_v[int(r['contributor_id'])] = count
                self.graph.vs[count]['id'] = int(r['contributor_id'])
                self.graph.vs[count]['label'] = r['contributor_name']
                self.graph.vs[count]['article_edits'] = 0
                self.graph.vs[count]['articles'] = {int(r['page_id'])}
                count += 1

            self.graph.vs[mapper_v[int(r['contributor_id'])]]['article_edits'] += 1
            self.graph.vs[mapper_v[int(r['contributor_id'])]]['articles'].add(int(r['page_id']))

            # A page gets serveral contributors
            if not int(r['page_id']) in user_per_page:
                user_per_page[int(r['page_id'])] = {int(r['contributor_id'])}
            else:
                if int(r['contributor_id']) not in user_per_page[int(r['page_id'])]:
                    user_per_page[int(r['page_id'])].add(int(r['contributor_id']))

        count = 0
        # Edges
        for _, p in user_per_page.items():
            for u1 in p:
                for u2 in p:
                    if u1 == u2:
                        continue
                    k_edge = (u1 << 32) + u2
                    k_edge_2 = (u2 << 32) + u1
                    if k_edge in mapper_e:
                        self.graph.es[mapper_e[k_edge]]['weight'] += 1
                        continue
                    elif k_edge_2 in mapper_e:
                        #self.graph.es[mapper_e[k_edge_2]]['weight'] += 1
                        continue

                    self.graph.add_edge(mapper_v[u1], mapper_v[u2])
                    mapper_e[k_edge] = count
                    count += 1
                    self.graph.es[mapper_e[k_edge]]['weight'] = 1
                    self.graph.es[mapper_e[k_edge]]['id'] = k_edge
                    self.graph.es[mapper_e[k_edge]]['source'] = u1
                    self.graph.es[mapper_e[k_edge]]['target'] = u2

        # total pages per user
        if 'articles' in self.graph.vs.attributes():
            articles = [len(node['articles']) for node in self.graph.vs]
            self.graph.vs['articles'] = articles

        # total pages
        self.graph['wiki_articles'] = len(user_per_page)
        self.graph['wiki_article_edits'] = len(dff.index)


    def get_metric_dataframe(self, metric):
        metrics = CoEditingNetwork.get_metrics_to_plot()

        if metrics[metric] in self.graph.vs.attributes()\
            and 'label' in self.graph.vs.attributes():

            df = pd.DataFrame({
                    'User': self.graph.vs['label'],
                    metric: self.graph.vs[metrics[metric]]
                    })
            return df

        return pd.DataFrame()


    def add_others(self, df):
        self.calculate_edits(df, 'talk')


    @classmethod
    def get_metrics_to_plot(cls) -> dict:
        cls.remove_directed_node_metrics(cls.NODE_METRICS_TO_PLOT)
        metrics = dict()

        for k in cls.NODE_METRICS_TO_PLOT.keys():
            metrics[k] = cls.NODE_METRICS_TO_PLOT[k]['key']
        return metrics


    @classmethod
    def get_metrics_to_show(cls) -> dict:
        metrics = cls.get_metrics_to_plot().copy()
        del metrics['Tenure in the wiki']
        return metrics


    @classmethod
    def get_metric_header(cls, metric: str) -> list:
        metrics = cls.get_metrics_to_plot()
        header = list()
        if metric in metrics:
            header = [{'name': 'Editor', 'id': 'User'}, 
                {'name': metric, 'id': metric}]

        return header


    @classmethod
    def get_user_info(cls) -> dict:
        return cls.USER_INFO


    @classmethod
    def get_network_stats(cls) -> dict:
        return cls.NETWORK_STATS


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
        desc['min_node_size'] = 'A low edition in articles'
        desc['max_node_size'] = 'A high edition in articles'
        desc['min_edge_size'] = 'A weak interaction in the wiki'
        desc['max_edge_size'] = 'A strong interaction in the wiki'
        return desc


    @classmethod
    def get_main_class_metric(cls) -> str:
        if 'Article edits' in cls.NODE_METRICS_TO_PLOT:
            return cls.NODE_METRICS_TO_PLOT['Article edits']
        else:
            return ''


    @classmethod
    def get_main_class_key(cls) -> str:
        metric = cls.get_main_class_metric()
        return metric['log'] if metric and 'log' in metric else ''