from __future__ import annotations
from typing import TypeVar, Generic, List, Sequence
from copy import deepcopy
from functools import partial
from random import uniform
import random
from statistics import mean,pstdev
from dataclasses import dataclass
import numpy as np
import rasterio
from typing import Iterator, Tuple, List, Iterable
from math import sqrt
import os

def zscores(original: Sequence[float]) -> List[float]:
  avg: float = mean(original)
  std: float = np.std(original)
  if std == 0: # return all zeros if there is no variation
    return [0] * len(original)
  return [(x - avg) / std for x in original]


class DataPoint:
  def __init__(self, initial: Iterable[float]) -> None:
    self._originals: Tuple[float, ...] = tuple(initial)
    self.dimensions: Tuple[float, ...] = tuple(initial)
  @property
  def num_dimensions(self) -> int:
    return len(self.dimensions)
  def distance(self, other: DataPoint) -> float:
    combined: Iterator[Tuple[float, float]] = zip(self.dimensions,other.dimensions)
    differences: List[float] = [(x - y) ** 2 for x, y in combined]
    return sqrt(sum(differences))
  def __eq__(self, other: object) -> bool:
    if not isinstance(other, DataPoint):
      return NotImplemented
    return self.dimensions == other.dimensions
  def __repr__(self) -> str:
    return self._originals.__repr__()

Point = TypeVar('Point', bound=DataPoint)
class KMeans(Generic[Point]):
  @dataclass
  class Cluster:
    points: List[Point]
    centroid: DataPoint
  def __init__(self, k: int, points: List[Point]) -> None:
    if k < 1: # k-means can't do negative or zero clusters
      raise ValueError("k must be >= 1")
    self._points: List[Point] = points
    #self._zscore_normalize()
# initialize empty clusters with random centroids
    self._clusters: List[KMeans.Cluster] = []
    for _ in range(k):
      rand_point: DataPoint = self._random_point()
      cluster: KMeans.Cluster = KMeans.Cluster([], rand_point)
      self._clusters.append(cluster)
#Changing to: randomly assigning all points to clusters, then generating centroids for each cluster!
  @property
  def _centroids(self) -> List[DataPoint]:
    return [x.centroid for x in self._clusters]
  def _dimension_slice(self, dimension: int) -> List[float]:
    return [x.dimensions[dimension] for x in self._points]
  def _zscore_normalize(self) -> None:
    zscored: List[List[float]] = [[] for _ in range(len(self._points))]
    for dimension in range(self._points[0].num_dimensions):
      dimension_slice: List[float] = self._dimension_slice(dimension) #PROBLEM!!!
      for index, zscore in enumerate(zscores(dimension_slice)):
        zscored[index].append(zscore)
    for i in range(len(self._points)):
      self._points[i].dimensions = tuple(zscored[i])
  def _random_point(self) -> DataPoint:
    rand_dimensions: List[float] = []
    for dimension in range(self._points[0].num_dimensions):
      values: List[float] = self._dimension_slice(dimension)
      rand_value: float = uniform(min(values), max(values))
      rand_dimensions.append(rand_value)
    return DataPoint(rand_dimensions)
  def _assign_clusters(self) -> None:
    for point in self._points:
      closest: DataPoint = min(self._centroids,key=partial(DataPoint.distance, point))
      idx: int = self._centroids.index(closest)
      cluster: KMeans.Cluster = self._clusters[idx]
      cluster.points.append(point)
  def _generate_centroids(self) -> None:
    for cluster in self._clusters:
      if len(cluster.points) == 0: # keep the same centroid if no points
        continue
      means: List[float] = []
      for dimension in range(cluster.points[0].num_dimensions):
        dimension_slice: List[float] = [p.dimensions[dimension] for p in cluster.points]
        means.append(mean(dimension_slice))
        cluster.centroid = DataPoint(means)
  def run(self, max_iterations: int = 10) -> List[KMeans.Cluster]:
    for iteration in range(max_iterations):
      if iteration != 0:
        for cluster in self._clusters: # clear all clusters
          cluster.points.clear()
        self._assign_clusters() # find cluster each point is closest to
        old_centroids: List[DataPoint] = deepcopy(self._centroids) # record
        self._generate_centroids() # find new centroids
        print(f"iteration #{iteration}- centroids: {[([round(h,2) for h in i.centroid._originals],len(i.points)) for i in self._clusters]}")
        if old_centroids == self._centroids: # have centroids moved?
          print(f"Converged after {iteration} iterations")
          return self._clusters
      else:
        for point in self._points:
          self._clusters[random.randint(0,len(self._clusters)-1)].points.append(point)
        self._generate_centroids()
        print(f"iteration #{iteration} centroids: {[([round(h,2) for h in i.centroid._originals],len(i.points)) for i in self._clusters]}")

    return self._clusters

point1: DataPoint = DataPoint([2.0, 1.0, 1.0])
point2: DataPoint = DataPoint([2.0, 2.0, 5.0])
point3: DataPoint = DataPoint([3.0, 1.5, 2.5])
kmeans_test: KMeans[DataPoint] = KMeans(2, [point1, point2, point3])
test_clusters: List[KMeans.Cluster] = kmeans_test.run()
for index, cluster in enumerate(test_clusters):
  print(f"Cluster {index}: {cluster.points}")
  
os.chdir('/Users/timothyclark/Documents/Python/remote_sensing/kmeansproject/')
file1 = 'no-0822.img'
file2 = 'no-0907.img'
class GeoPixel(DataPoint):
  def __init__(self,coord,composite):
    super().__init__(composite)
    self.coord = coord

def parser(imgfile,band):
  a = rasterio.open(imgfile)
  pixels = a.read(band)
  a.close()
  return pixels

def composite(imgarray):
  szx,szy = imgarray[0].shape[0], imgarray[0].shape[1]
  comp = np.zeros((szx,szy,len(imgarray)),dtype=np.float16)
  for index,band in enumerate(imgarray):
    comp[:,:,index] = band
  lst = []
  for x in range(szx):
    for y in range(szy):
      lst += [GeoPixel((x,y),list(comp[x,y,:]))]
  return lst

#z = composite([parser(file1,i+1) for i in range(6)] + [parser(file2,i+1) for i in range(6)])
z = composite([parser(file1,5),parser(file2,5)])
print(len(z))
print(z[int(uniform(0.0,float(len(z))))])
input()

kmeans_test2: KMeans[GeoPixel] = KMeans(5,z)
clusters: KMeans.Cluster = kmeans_test2.run()
for index, cluster in enumerate(clusters):
  print(f"Cluster {index}: {len(cluster.points)}")
  
input()

def class2array(refimg,clusters,newfile):
    params = rasterio.open(refimg,'r')
    sz = params.read(1).shape
    newraster = np.zeros((sz[0],sz[1],3),dtype=np.int8)
    for index, cluster in enumerate(clusters):
        for point in cluster.points:
            newraster[point.coord[0],point.coord[1],:]= (255/len(clusters)-1)*index
    write = rasterio.open(f'{newfile}-kmeans.tif','w',
        driver='GTiff',
        height=newraster.shape[0],
        width=newraster.shape[1],
        count=3,
        dtype=np.int8,
        crs=params.crs,
        transform=params.transform)
    for h in range(3):
        write.write(newraster[:,:,h],h+1)
    params.close()
    write.close()
    return newraster

n = class2array(file1,clusters,'4class')
print(n[50:55,50:55,:])

