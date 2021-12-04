"""!
@PyMid is devoted to manage multitask algorithms and methods.

@authors Michel Pires da Silva (michelpires@dcc.ufmg.br)

@date 2014-2018

@copyright GNU Public License

@cond GNU_PUBLIC_LICENSE
    PyMid is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    PyMid is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endcond
"""
"""!
@PyMid is devoted to manage multitask algorithms and methods.

@authors Michel Pires da Silva (michelpires@dcc.ufmg.br)

@date 2014-2018

@copyright GNU Public License

@cond GNU_PUBLIC_LICENSE
    PyMid is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    PyMid is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endcond
"""
from core.managers.worker import BaseWorkerInfo

import pandas as pd
import warnings
warnings.filterwarnings('ignore')


#used to generate pivotal matrix, if necessary (__preprocessing + __generate_model)
class config:
    BASEDPATH   = '/Users/michel/Dropbox/Doutorado/datasets/ml-small/'
    RATING      = 'ratings.csv'
    MOVIES      = 'movies.csv'


class MOVIELENS(BaseWorkerInfo):
    
    def __init__(self, train, n):
        self.__number_of_results = n
        self.__matrix = pd.read_csv(train, delimiter=',')
        self.__movies = self.__preprocessing()
        self.__cache = {}
        
    def __preprocessing(self):
        rating = pd.read_csv(config.BASEDPATH+config.RATING, delimiter=',')
        movies = pd.read_csv(config.BASEDPATH+config.MOVIES, delimiter=',', usecols=['movieId','title'])
        rating = pd.merge(rating, movies, on='movieId')
        movies = pd.DataFrame(rating.groupby('title')['rating'].mean())
        movies['number_of_ratings'] = rating.groupby('title')['rating'].count()
        return movies

    
    def __generate_model(self, rating):
        return rating.pivot_table(index='userId', columns='title', values='rating')
        

    def __content_based_filter(self, user):
        correlation = None

        results = []
        for movie in user:
            
            rule = self.cache.get(movie)
            
            if isinstance(rule, int):
            
                tmp = self.__matrix[movie].dropna()
                similar = self.__matrix.corrwith(tmp).dropna()
                if not similar.empty:
                    correlation = pd.DataFrame(similar, columns=['correlation'])
                    correlation = correlation.join(self.__movies['number_of_ratings'])
                    correlation = correlation[correlation['number_of_ratings'] > 10].sort_values(by='correlation', ascending=False).head(self.__number_of_results)
                    results.append(correlation.index)
                    self.cache.set(movie, correlation.index)
                
                else:
                    self.cache.set(movie, '')
                    self.info_cache['missing'] += 1
            
            elif not isinstance(rule, str): 
                results.append(rule)
                self.info_cache['hits'] += 1
            
            else:
                self.info_cache['hits'] += 1
                    
        return results[0].tolist()
    
    
    def execute_task(self, task):
        user = list(filter(lambda x: x == x, task))
        self.__content_based_filter(user[2:])
        
        


