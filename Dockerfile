FROM kbase/kbase:sdkbase.latest
MAINTAINER KBase Developer
# -----------------------------------------

# Insert apt-get instructions here to install
# any required dependencies for your module.

# RUN apt-get update

# -----------------------------------------


RUN mkdir -p /kb/module/dependencies/bin

WORKDIR /kb/module/dependencies/bin
RUN curl -o blast.tar.gz 'ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.2.30/ncbi-blast-2.2.30+-x64-linux.tar.gz'
RUN tar -zxvf blast.tar.gz ncbi-blast-2.2.30+/bin/makeprofiledb ncbi-blast-2.2.30+/bin/rpsblast
RUN mv ./ncbi-blast-2.2.30+/bin/makeprofiledb ../bin/makeprofiledb.linux
RUN mv ./ncbi-blast-2.2.30+/bin/rpsblast ../bin/rpsblast.linux
#RUN rmdir ./ncbi-blast-2.2.30+/bin
#RUN rmdir ./ncbi-blast-2.2.30+
#RUN rm ./blast.tar.gz

WORKDIR /kb/module/dependencies/bin
RUN curl -o hmmer.tar.gz 'http://eddylab.org/software/hmmer3/3.1b1/hmmer-3.1b1-linux-intel-x86_64.tar.gz'
RUN tar -zxvf hmmer.tar.gz hmmer-3.1b1-linux-intel-x86_64/binaries/hmmscan hmmer-3.1b1-linux-intel-x86_64/binaries/hmmpress
RUN mv ./hmmer-3.1b1-linux-intel-x86_64/binaries/hmmscan ../bin/hmmscan.linux
RUN mv ./hmmer-3.1b1-linux-intel-x86_64/binaries/hmmpress ../bin/hmmpress.linux
#RUN rmdir ./hmmer-3.1b1-linux-intel-x86_64/binaries
#RUN rmdir ./hmmer-3.1b1-linux-intel-x86_64
#RUN rm ./hmmer.tar.gz

WORKDIR /kb/module/dependencies/bin
RUN curl -o muscle3.8.31_i86linux64.tar.gz 'http://www.drive5.com/muscle/downloads3.8.31/muscle3.8.31_i86linux64.tar.gz'
RUN tar -zxvf muscle3.8.31_i86linux64.tar.gz

WORKDIR /kb/module/dependencies/bin
RUN curl -o mga_x86_64.tar.gz 'http://metagene.nig.ac.jp/metagene/mga_x86_64.tar.gz'
RUN tar -zxvf mga_x86_64.tar.gz
#RUN mv mga_linux_ia64 ../bin

WORKDIR /kb/module/dependencies/bin
RUN curl -o mcl-14-137.tar.gz 'http://www.micans.org/mcl/src/mcl-14-137.tar.gz'
RUN tar -zxvf mcl-14-137.tar.gz
RUN cd ./mcl-14-137 && ./configure --prefix=`pwd`../../bin \
	&& make \
	&& make install
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod 777 /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
