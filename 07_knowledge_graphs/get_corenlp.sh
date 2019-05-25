#!/bin/sh

#export REL_DATE="2018-10-05"

#wget http://nlp.stanford.edu/software/stanford-corenlp-full-${REL_DATE}.zip
#unzip stanford-corenlp-full-${REL_DATE}.zip

#mv stanford-corenlp-full-${REL_DATE} CoreNLP
#rm stanford-corenlp-full-${REL_DATE}.zip
#cd CoreNLP

#wget http://nlp.stanford.edu/software/stanford-corenlp-models-current.jar

export CLASSPATH="`find . -name '*.jar'`"
