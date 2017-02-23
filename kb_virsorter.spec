/*
A KBase module: kb_virsorter
This module wraps the virsorter pipeline.
*/

module kb_virsorter {


    typedef structure {
        string assembly_ref;
    } VirsorterParams;

    typedef structure {
        string report_name;
        string report_ref;
    } VirsorterResults;
	
    /*
        Identify viral sequences in microbial reads
    */
    funcdef run_virsorter(VirsorterParams params) returns (VirsorterResults) authentication required;
};
