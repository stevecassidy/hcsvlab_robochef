import logging

from hcsvlab_robochef.cooee.ingest import *
from hcsvlab_robochef.ace.ingest import *
from hcsvlab_robochef.ice.ingest import *
from hcsvlab_robochef.monash.ingest import *
from hcsvlab_robochef.griffith.ingest import *
from hcsvlab_robochef.md.ingest import *
from hcsvlab_robochef.auslit.ingest import *
from hcsvlab_robochef.braided.ingest import *
from hcsvlab_robochef.art.ingest import *
from hcsvlab_robochef.paradisec.ingest import *
from hcsvlab_robochef.eopas_test.ingest import *
from hcsvlab_robochef.avozes.ingest import *
from hcsvlab_robochef.pixar.ingest import *
from hcsvlab_robochef.austalk.ingest import *
from hcsvlab_robochef.rirusyd.ingest import *


def main():
    """
    Primary application entry point
    """
    corpora = utils.getCorporaArgs(sys.argv)

    print "cpr: corpora conversion tool\n"

    # NOTE: Configure the logger and the configuration manager
    configmanager.configinit()
    logging.basicConfig(filename='hcsvlab_robochef.log', level=logging.INFO, format='%(asctime)s %(message)s')

    corpus_basedir = configmanager.get_config("CORPUS_BASEDIR", "../input/")
    output_dir = configmanager.get_config("CORPUS_OUTPUTDIR", "../output/")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for c in corpora:

        if c == "art":
            print "converting ART"
            art = ARTIngest()
            art.setMetaData(corpus_basedir + "ART/ART-corpus-catalogue.xls")
            art.ingestCorpus(corpus_basedir + "ART", output_dir + "ART")

        elif c == "cooee":
            print "converting COOEE"
            cooee = CooeeIngest()
            cooee.setMetaData(corpus_basedir + "COOEE/COOEE.XLS")
            cooee.copy_collection_metadata(corpus_basedir, output_dir, "cooee.n3", "cooee.n3")
            cooee.ingestCorpus(corpus_basedir + "COOEE/data", output_dir + "cooee")

        elif c == "ace":
            print "converting ace"
            ace = ACEIngest()
            ace.setMetaData(corpus_basedir + "ace/Manual")
            ace.copy_collection_metadata(corpus_basedir, output_dir, "ace.n3", "ace.n3")
            ace.ingestCorpus(corpus_basedir + "ace", output_dir + "ace")

        elif c == "ice":
            print "converting ice"
            ice = ICEIngest()
            ice.copy_collection_metadata(corpus_basedir, output_dir, "ice.n3", "ice.n3")
            ice.ingest(os.path.join(corpus_basedir, "ICE"), os.path.join(output_dir, "ice"))

        elif c == "monash":
            print "converting monash"
            monash = MonashIngest()
            monash.copy_collection_metadata(corpus_basedir, output_dir, "monash.n3", "monash.n3")
            monash.ingestCorpus(corpus_basedir + "Monash Corpus of Australian English/Transcripts-sanitised",
                                output_dir + "monash")

        elif c == "griffith":
            print "converting griffith"
            griffith = GriffithIngest()
            griffith.setMetaData(corpus_basedir + "griffith/metadata")
            griffith.copy_collection_metadata(corpus_basedir, output_dir, "gcsause.n3", "gcsause.n3")
            griffith.ingestCorpus(corpus_basedir + "griffith", output_dir + "griffith")

        elif c == "md":
            print "converting mitchell & delbridge"
            md = MDIngest()
            md.setMetaData(corpus_basedir + "MD/flatfilesrc.txt")
            md.copy_collection_metadata(corpus_basedir, output_dir, "md.n3", "mitcheldelbridge.n3")
            md.ingestCorpus(corpus_basedir + "MD", output_dir + "md")

        elif c == "auslit":
            print "converting auslit"
            auslit = AuslitIngest()
            auslit.copy_collection_metadata(corpus_basedir, output_dir, "austlit.n3", "austlit.n3")
            auslit.ingestCorpus(corpus_basedir + "AusLit", output_dir + "auslit")

        elif c == "braided":
            print "converting braided channels"
            braided = BraidedIngest()
            braided.copy_collection_metadata(corpus_basedir, output_dir, "braided_channels.n3", "braidedchannels.n3")
            braided.ingestCorpus(corpus_basedir + "braided_channels", output_dir + "braided")

        elif c == "paradisec":
            print "converting paradisec"
            paradisec = ParadisecIngest()
            paradisec.ingestCorpus(corpus_basedir + "paradisec", output_dir + "paradisec")

        elif c == "eopas_test":
            print "converting eopas_test"
            eopas = EopasTestIngest()
            eopas.ingestCorpus(corpus_basedir + "eopas_test", output_dir + "eopas_test")

        elif c == "avozes":
            print "converting avozes"
            avozes = AvozesIngest()
            avozes.setMetaData(corpus_basedir + "avozes/Avozes.xls")
            avozes.ingestCorpus(corpus_basedir + "avozes", output_dir + "avozes")

        elif c == "pixar":
            print "converting Pixar Film Excerpts"
            pixar = PixarIngest()
            pixar.setMetaData(corpus_basedir+"pixar/PixarFilmExcerpts.xls")
            pixar.copy_collection_metadata(corpus_basedir, output_dir, "pixar.n3", "pixar.n3")
            pixar.ingestCorpus(corpus_basedir+"pixar", output_dir+"pixar")

        elif c == "austalk":
            print "converting austalk"
            austalk = AustalkIngest()
            austalk.ingestCorpus(corpus_basedir + "austalk", output_dir + "austalk")

        elif c == "rirusyd":
            print "converting Room Impulse Response"
            rir = RirIngest()
            rir.setMetaData(corpus_basedir+"rirusyd/room_impulse_responses.xlsx")
            rir.copy_collection_metadata(corpus_basedir, output_dir, "rirusyd.n3", "rirusyd.n3")
            rir.ingestCorpus(corpus_basedir+"rirusyd", output_dir+"rirusyd")

if __name__ == "__main__":
    main()
