# Wikipedia articles about members of the German Bundestag (extended)

> **Date:** 28.04. *(Due: 29.04.)*  
> **Name:** `PhTr` Philipp Trenz  
> **Code:** [git](https://github.com/philipptrenz/Text-Visualisation-in-Practice/tree/master/03_dimension_reduction)  
> **Session:** [Dimensionality Reduction+PCA+tSNE+ Visualization](../index)

----

## Intro

The last session was focused on generating high dimensional data using the [tf-idf](https://en.wikipedia.org/wiki/Tf–idf) algorithm. Therefore the Wikipedia articles of all current 709 members of the German Bundestag got parsed and used as a database for the algorithm. In this this session, the focus is on reducing dimensions to 2 or 3 while keeping the containing information as high as possible. 

## Approach description

In the lecture some algorithms for the reduction of dimensions were presented, among others [PCA](https://en.wikipedia.org/wiki/Principal_component_analysis) and [t-SNE](https://en.wikipedia.org/wiki/T-distributed_stochastic_neighbor_embedding). The Machine Learning framework _scikit-learn_, which was already used to calculate the tf-idf vectors for the Wikipedia articles, also provides implementations for both of the algorithms. 

As the _TfidfVectorizer_ interface of the framework generates a sparse dataset, which is not compatible to the PCA implementation in this form, for a first inquiry the t-SNE interface was used.

Since the database was created on the basis of [this](https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Deutschen_Bundestages_(19._Wahlperiode)#Abgeordnete) Wikipedia table, in addition to the names of the members of the German Bundestag and the cross-references to the respective Wikipedia articles, the columns on party affiliation, year of the politician and state of origin were recorded. These data are now used to discover interesting relationships based on the tf-idf vector data reduced with t-SNE.

## Show result(s)

The following plot shows the result of the dimensionality reduction to 2d with the t-SNE algorithm, while the colors represent age groups of the members. 

![t-sne plot per age](img/tsne_plot_per_age.png)

![t-sne plot per state](img/tsne_plot_per_state.png)

![t-sne plot per party](img/tsne_plot_per_party.png)

![t-sne plot per party with article size](img/tsne_plot_per_party_with_article_size.png)

![t-sne 3d plot per party](img/tsne_3d_plot_per_party.png)

## Discuss findings/hypothesis
