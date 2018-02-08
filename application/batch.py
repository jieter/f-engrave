from util import fmessage


class Batch(object):

    def __init__(self, settings):

        self.settings = settings

        fmessage('(F-Engrave Batch Mode)')

        if settings.get('input_type') == "text":
            pass
            # self.readFontFile(self.settings)
        else:
            pass
            # self.read_image_file(self.settings)

        # self.do_it()
        # if self.cut_type.get() == "v-carve":
            # self.v_carve_it()
        # self.WriteGCode()
        # self.WriteSVG()

        # for line in svgcode:
            # print line

        # for line in gcode:
        #     try:
        #         sys.stdout.write(line+'\n')
        #     except:
        #         sys.stdout.write('(skipping line)\n')
