from util import fmessage


class Batch(object):

    def __init__(self, settings):

        self.settings = settings

        fmessage('(F-Engrave Batch Mode)')

        if settings.get('input_type') == "text":
            pass
            # self.Read_font_file()
        else:
            pass
            # self.Read_image_file()

        # self.DoIt()
        # if self.cut_type.get() == "v-carve":
            # self.V_Carve_It()
        # self.WriteGCode()
        # self.WriteSVG()

        # for line in self.svgcode:
            # print line

        # for line in self.gcode:
        #     try:
        #         sys.stdout.write(line+'\n')
        #     except:
        #         sys.stdout.write('(skipping line)\n')
