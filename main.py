from flask import Flask, request
from Motility import semenAnalysis
from viability import semenViability
from Utility.Check_req_iterations_from_file import should_we_proceed
from pprint import pprint
import shutil
import os
import timeit

app = Flask(__name__)

transfer_to_front_start = 0

upload_folder = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "upload")
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

allowed_extensions = ['jpg']


def is_allowed_file(a): return '.' in a and a.rsplit(
    '.', 1)[1].lower() in allowed_extensions


@app.route("/via", methods=['POST'])
def via():
    try:
        if 'file' not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == '':
            return "No selected file"
        if not is_allowed_file(file.filename):
            return "Extension is invalid"

        filename = file.filename
        pid = request.form['code']
        if not os.path.exists(os.path.join(upload_folder, pid)):
            os.mkdir(os.path.join(upload_folder, pid))
        file.save(os.path.join(upload_folder, pid, filename))
        return ""
    except:
        print("Error in upload")
        return "ERROR"


@app.route("/sendok", methods=["POST"])
def okSignal():
    pid = request.form["code"]
    if os.path.exists(os.path.join(upload_folder, pid)):
        shutil.rmtree(os.path.join(upload_folder, pid))
    return "OK"


@app.route("/viafinalize", methods=['POST'])
def viafinalize():
    pid = request.form['code']
    # path = request.form['file']
    folder = os.path.join(upload_folder, pid)
    Path = os.path.join(upload_folder, pid, "image.jpg")
    #Path = "C:\\Users\\ETC\\Desktop\\ViaImage\\*.jpg"
    viab = semenViability()
    live, death = viab.viabilityAnalysis(Path)
    # result,_ = function(raw_result)
    live_xy = []
    death_xy = []
    for xy in live[0]:
        live_xy.append(xy[0][0])
    for xy in death[0]:
        death_xy.append(xy[0][0])

    live_point = ""
    death_point = ""

    for xy in live_xy:
        pnt = Point(xy[0], xy[1])
        live_point += pnt.serialize() + ","
    for xy in death_xy:
        pnt = Point(xy[0], xy[1])
        death_point += pnt.serialize() + ","

    result = '{"cells": {'
    result += '"alive":[' + live_point[:-1] + ']'
    result += ',"death":[' + death_point[:-1] + ']'
    result += "} }"

    return result


@app.route("/", methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'GET':
            return "Everything is OK (CASA server)"
        if 'file' not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == '':
            return "No selected file"
        if not is_allowed_file(file.filename):
            return "Extension is invalid"

        filename = file.filename
        pid = request.form['code']
        if not os.path.exists(os.path.join(upload_folder, pid)):
            os.mkdir(os.path.join(upload_folder, pid))
        file.save(os.path.join(upload_folder, pid, filename))
        return ""
    except:
        print("Error in upload")
        return "ERROR"


@app.route("/hasresult", methods=['POST'])
def hasResult():
    pid = request.form['code']
    folder = os.path.join(upload_folder, pid)
    file = os.path.join(folder, "result.txt")
    if os.path.exists(file):
        return "1"
    return "0"


@app.route("/getresult", methods=['POST'])
def getResult():
    pid = request.form["code"]
    file1 = os.path.join(upload_folder, pid, "result.txt")
    if os.path.exists(file1):
        res = ""
        with open(file1, 'r+') as filex:
            res = filex.read()
        return res
    return ""


@app.route("/finalize", methods=['POST'])
def finalize():
    if not should_we_proceed('deactive'):
        return None
    else:
        Preprocessing_start = timeit.default_timer()

        print("Finalize request")
        pid = request.form['code']
        nframe = int(request.form['nframe'])
        fps = int(request.form['fps'])
        min_size_thr = float(request.form['min_size_thr'])
        max_size_thr = float(request.form['max_size_thr'])
        pixel_per_micro = float(request.form['pixel_per_micro'])
        vcl_thr = float(request.form['vcl_thr'])
        lin_thr = float(request.form['lin_thr'])
        str_thr = float(request.form['str_thr'])
        vsl_rapid_thr = float(request.form['vsl_rapid_thr'])
        n_thr = float(request.form['n_thr'])
        sdv_deb = float(request.form['sdv_deb'])
        obs_flag = float(request.form['obs_flag'])
        mot_dur = float(request.form['mot_dur'])



        folder = os.path.join(upload_folder, pid)
        path = os.path.join(upload_folder, pid, "*.jpg")

        # # TODO it is not the ideal solution, may cause problems in the front in case of a rerun of the test
        if os.path.isfile(os.path.join(folder, 'result.txt')):
            return "READY"

        with open(os.path.join(folder, 'result.txt'), 'w+') as fs:
            fs.write("")

        Preprocessing_stop = timeit.default_timer()
        print('Preprocessing Time = ', Preprocessing_stop - Preprocessing_start)
        total_Processing_start = timeit.default_timer()

        mot = semenAnalysis()
        print('******* calling primary process function *******')
        # if 'head_calibre' in request.form:
        #    print('HERE')

        # if (request.form['head_calibre'] != "" | request.form['head_calibre'] !="0"):
        #     head_calibre = float(request.form['head_calibre'])
        #     min_size_thr = (head_calibre/2)*3.14*(head_calibre/10)
        #     max_size_thr = (head_calibre/2)*3.14*(head_calibre/2)

        raw_result = mot.semenMotilityAnalysis(path, nframe, fps, folder, min_size_thr, max_size_thr, pixel_per_micro,
                                               vcl_thr, lin_thr, str_thr, vsl_rapid_thr, n_thr, sdv_deb, obs_flag,
                                               mot_dur)
        result, _ = function(raw_result)


        return "READY"


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def serialize(self):
        return '{{"x":"{0}","y":"{1}"}}'.format(self.x, self.y)


class Cell:
    def __init__(self, path, ctype, VCL, VAP, VSL, STR):
        self.path = path
        self.ctype = ctype
        self.VCL = VCL
        self.VAP = VAP
        self.VSL = VSL
        self.STR = STR


    def serialize(self):
        s_path = ""
        for point in self.path:
            s_path += point.serialize() + ","
        s_path = s_path[:-1]
        return '{{"type":"{0}","path":[{1}],"VCL":"{2}","VAP":"{3}","VSL":"{4}","STR":"{5}"}}'.format(
            self.ctype, s_path, self.VCL, self.VAP, self.VSL, self.STR, )


def function(data):
    cells = []
    # TODO TypeError: list indices must be integers or slices, not str
    for sperm, params in zip(data["Prog"], data["ProgParam"]):
        path = []
        for i in range(0, len(sperm[0])):
            x = sperm[0][i]
            y = sperm[1][i]
            path.append(Point(x, y))
        cells.append(
            Cell(path, "PROG", params[0], params[1], params[2], params[3], params[4], params[5], params[6], params[7],
                 params[8]))

    for sperm, params in zip(data["NonProg"], data["nonProgParam"]):
        path = []
        for i in range(0, len(sperm[0])):
            x = sperm[0][i]
            y = sperm[1][i]
            path.append(Point(x, y))
        cells.append(
            Cell(path, "NPROG", params[0], params[1], params[2], params[3], params[4], params[5], params[6], params[7],
                 params[8]))

    for sperm, params in zip(data["Immotile"], data["immotileParam"]):
        path = []
        for i in range(0, len(sperm[0])):
            x = sperm[0][i]
            y = sperm[1][i]
            path.append(Point(x, y))
        cells.append(
            Cell(path, "IMMO", params[0], params[1], params[2], params[3], params[4], params[5], params[6], params[7],
                 params[8]))

    json = '{"cells":['
    for cell in cells:
        json += cell.serialize() + ","
    json = json[:-1]
    json += "]}"

    return json, cells


resp_array = [
    "BAA17C3D614BC75AD136699CAB6F6F1B",
    "ADE069FD1408F01B5A967CDDD2332EBB",
    "11C70D3B6D6146243117770A64234209",
    "DA754CA47C9754C556142B64D43410A2",
    "DCE3DE434E83C636413B1807EBD4BCFE",
    "2DCD05335076CE2968FC62F344AE0AD3",
    "1DBD8457050E129147D70DC760579034",
    "0FFDCAE0F61755E6A6D5DF3FB87D65BF",
    "E9672D7BD08AB499DB45384230AFA8C0",
    "FD1667FDE5A8B337A772EE7C2570BA63",
    "19BD3DAB6DEB275EA3D2FB6FFECB1DC7",
    "40CC19F0B4DA3E0D8664CF76AFC4A095",
    "14A80ED190C5C73451E369EE35DFEB26",
    "54B34ECAB220873311EA29E558DCC8E6",
    "0AB084995511DE340AFC020635482CF6",
    "2982B068D13F468273C639D0174E8C8A",
    "63E03ADC89FEDC69A583EC12CF49A6B5",
    "81582B33B9E2FF7DDBBBA22AA126B9E8",
    "681C4264E3DE8B992D4F25423FB31869",
    "3D87A46D2538728767FD2DED4E8A3580",
    "232C96B29AC561D0C1538309DA98D8A0",
    "34056E790EA069D36E61A45EB00A4468",
    "CB5A5131F7E4A57B91B9D82864804AB7",
    "A67C00D3206118DCBC55677DE5FCD577",
    "05F7610B1151525445E71E8FFF5DAF46",
    "D27A74D574674CD62D391373623BD319",
    "07B45E08F5D2F805C16C887E1E6BC40A",
    "ECD076BB966D84F4B630FFA21B9050CC",
    "60911AEC7A373D663AD54E44CB5B4C0F",
    "7704A29AAEED3DF874E5B721EE6D6926",
    "6A6D7C93B22689CA2F9D1B13D73FE250",
    "EF61750CEBDB8126B563FC73848BB34A",
    "566E0F528276CAE5930FDA9FB2B4997D",
    "EFCCD6EFB72FCE9A599610AC36A63C6C",
    "1C9116E8D6ACFF1D59C871C78D8C1200",
    "A65BDDA7BCE2FC91FCA05A44E00D5A3A",
    "A4755FC99FC167E4C0ACD9D584B14EE5",
    "141A0E786EA349D24E606C93D3BFDE35",
    "65C47F462F847F03EB0E8334D4E90448",
    "602E1A547A8F3DFE3A4CE0BB47CE24AC",
    "6A2E7FBA2FF87F3FEB328300281BC507",
    "A1ECB81483555548E41FDF92ADB924B0",
    "1C2B16513A35FFB45962716D29EAB6EC",
    "B79F372DE7A54F989851B1A9E8B2D9CC",
    "364C91E35151AB8C038FF62D06A9A0E6",
    "C59D9F2F338BBB3E03574947288B72C6",
    "463DE113C02E389DA61A863CBEE8DC8F",
    "9A43F41925918EB45A7D7285F33E3918",
    "9E72C64AA788FE3F693200002BD6B84D",
    "3B21FEBDE2C879DBE51EEB1C65791CBB",
    "F5307D6A2DA8671FE312BB204E45EC15",
    "E8735EDE6E6C66DFB624397A44D10433",
    "1E9110E81372FD1D5BC877C78450F703",
    "BE65B79B07C256D2E185DA0B6BDFFDA9",
    "E0CD0AA89A7E90C1BA078397C6E20C5B",
    "D5825F68CD3FAB828FC6D6D01CE7E141",
    "468F1D4B0D8B073E8333DB0F9C58B3E0",
    "5052F7FDF64FC9FE5AFB905B748CEB45",
    "25077CBAD31C9A4BE3DDAACDD05399D1",
    "998C90F564717DEFDBBEF0305C2AD7B6",
    "BEFEE951D8E030533F248EFFF790C04D",
    "C7B4990835D2B905016C4F7EC1DA2CEB",
    "4B944160219E7B09EF04873AA94C252E",
    "F1137BFAE9AD8F34AB71F2618E8D896F",
    "BD78EAD7D96533D087A08D7184386D11",
    "99F45DE9401C24EF4AE448305E77D2FD",
    "31CE966156D0AE03F631F1AFA3B3D660",
    "422F3853588E090C0E3F0DB2DC97734C",
    "F8E3628AE25C88A3A2E1EBF1AD7BD217",
    "36E7BD8E2C5849A76C1D348DB1FD49A1",
    "6B29AEB553C029D313B1BB04A071607F",
    "92298955E88CC0FFC84DEF84703FBCED",
    "1259B5F0B4428FF1247AD2504952AC67",
    "ECA6263C2B4AB159CCBC3383E5634417",
    "89D54DC8703FD40E673158D0DAC81887",
    "1D7CD862C494A37AD38DCEBC45B31C6D",
    "20A1953D9F4B6C5AE526809C6D06FFF8",
    "BC26159BA83F32AA7AC2C3EC5F14F6DF",
    "6FD7072B7771422435173E5A08E03733",
    "DE74D78C05D63CF19BA4B02AA269AF2D",
    "1735C2A9CEDC5DAF7D79D770511E7C52",
    "E90E5D206D13674281113AE03B9CB781",
    "C9DD83EF3FCB477E0F965507E4253BD2",
    "0D0E6576D264EE6E483902B0509E2E2C",
    "8E4C38E30851008C07FD5F2DB2A937D7",
    "79FC098879C6337197FFCF42CD03FEE7",
    "111D98F809AF6E324B771167D8F1BAF8",
    "FEC664ADE47BB2C6A402EDACE5015945",
    "D84CD1B431163AA99D7FB672C0B17D31",
    "E162730EA3840BBFDC76F5888917C1A4",
    "E80C1734C7BAA67082389B4285420518",
    "BCE9662706661ED18A5FA0E300EBBDE1",
    "76662F5AE27FEBEAB002F9AC31E0BD83",
    "053073B3A33B0BE2DCAAF5D3C6976963",
    "768D2CF04C2B256A12D9BF44D850F05C",
    "26BF1373C37AA8217CEB951365CD7875",
    "F79A7D70E32789BAADFEF4E83E699A62",
    "26B0932E9D586A2B3AAE868DE84BA40D",
    "3C4836B08060DFD57980510E0D0060F1",
    "1BC88C67B3D2940140A3EBA12110ACAF",
    "B9482323A1F2C15DF59BBC0ABA63232D",
    "1DFE1506AC73FE7E582972A04546656B",
    "04C6AFAD3E7B7BC65E0226ACD1AA289B",
    "0DDC69220978602B571E6403C760B311",
    "AC52E46E584B22FE6A1632806CE639BD",
    "8D1617FDB5A8FD07D942A06CBF17B908",
    "B52961B56CC0F8D3C58A7404FA4D8723",
    "18E0838B025D17A442E00AF23E30900B",
    "4C9026ED5634216716DAA449F6605907",
    "63F3C45EFBEDDC58211BA3FA214E5033",
    "7A126C6A778C99933F450B44AA79D072",
    "701F2A634ABE2DED2A5F9F2E09DA6358",
    "BD76144AAB6F33DA7B32C2BC4C2BA5AF",
    "DFB24F9D7FAC511F916D28BB3A10E34A",
    "E5E37FDDBFD507C8E080F9F9ECD489CB",
    "191080FB01AA163543700962CAB92148",
    "D24274ED745F4C8EE269132BB81A1031",
    "5998C0724125D6BC03F849EA699824AE",
    "0FDCCAC1F63455074E7ADFD96CD044A0",
    "BEEA2481A457CCBAEEFEB7E8F068949E",
    "62BF74C656E0913F27EE13E1BFD61F39",
    "8E7CC6407A6500DC483410A6A84CCA40",
    "A650DDAEBCF5FCA8FC9BF0252D3899C3",
    "D6824DFF2D2A8C598CE88EA7D6DB0BAE",
    "A733A97E0877F52E31E62F185745828A",
    "CF8B5561CB34A18B95C9DCD9FA084724",
    "B5E5AC1B6E3C5351E604DD8B56632477",
    "B5F8EFC4A3E62B5173BB392AC137E3F1",
    "306B69552570A9E7F609BF992031D3AF",
    "51A0D84A491D2E640BA0513111E5D08E",
    "6EDDF5B8146E01F134377CA7333401B9",
    "845322FE024C7AFF723E455A6D6DB5B7",
    "7311D43FEB0AECB9423CB31833AC92B7",
    "45D0517031AE4B19DF14972AAED0CFA6",
    "94568DAEF1BA70A7C771FC78DDD337CD",
    "240B3E71BA05D7946142594D7C7C9A3A",
    "E4BDBD437C4AF341370B2D7323D0D034",
    "60121A607ABB3DEA3A58F5DB5BDE4C60",
    "9927E6D287109E8709B52089A57384E6",
    "99425DA040D724A679C8487FC52EEAA7",
    "3D4B7FF1BFF907ACE065F99D3E85AEC8",
    "E302B5BF091B5D4E25A66337AAE9BEE1",
    "289EF846A984FE03690E0034A63C303A",
    "5590DC7A4D2D2AB40FF055E25A41E6FE",
    "A04606E9265B1E8A13D96157B0871906",
    "4DA3A4DA7F7CAE0308DAC3D585247447",
    "4169E4A4352ABE116ADB62234FCABAA9",
    "EE8AA6361A906AD6323E7AA8B5638D49",
    "887C4A627795D567A4A85FB9083684D5",
    "2A2961E801261B918F9FA7A3AEB469C1",
    "8EFE0DA67DE4375393D9CB643C57B7D5",
    "F7C3A9FD65D9690831617F7168D1839F",
    "CE0DA571D4A8A4DB946914066B1A7946",
    "7E34704C6C029DB13B67176ABCBEAEFF",
    "8551486F38AF4EE9DA6790DBB1C62591",
    "609A7AE311E7931A25CD1DDCBAF9B211",
    "C626BD5CDC879CF69C44BA1B90EF0322",
    "FDEB9617F94DB120A713403EFE2531E2",
    "0F549A3F0B16606955AF133E690AF9E4",
    "6D33F4DA158D021437517D417227BCEE",
    "EACF70A6907086CFB005F995BEEEAC9A",
    "920A8988E8D3C0C2C870C99FB52A3C3E",
    "61FC1D027D583C4B3BFE49118ED4D578",
    "3CA656DB0606717566C45E5DD9E4687F",
    "EBE9C20FB9DA0B75AE20A5AFC3F175D7",
    "44595E9F413BB7C60191391F921B957A",
    "8EB7E5CA9411E484D4B78DFDE758DB69",
    "2B16643E047F10AAF4A6A29C15352A61",
    "77B3D09E97ADF22813F9CD8AC665A61D",
    "40CBAC090D81F6A4326D2A95B1FA1404",
    "B8E43F1CFF924789A040B9BA2DAA34A8",
    "BFE9B60F92A85F75FA20D1AFB8B2FE89",
    "6785F26F132618B93DFF7BEFB388612B",
    "A1E8B810F95D5574E423DFAE1504180D",
    "70C7A4A4752AFE112ADB22238FE02083",
    "613288D9198C1E133B56014025E2110E",
    "350A26FB463BDE6E49E2E05F4A3E35D9",
    "7344A65AAAAD31B8882AB361996F4555",
    "7B92E678672F34B221F66FE01F6CD207",
    "2209346FE526D1966740534FC9C9DA4C",
    "D9E34D4E7DFD5768CC4B2ACA4DDD2B4F",
    "2F57BA3E2BE9406875AC333DE4C2E48B",
    "06131869B7A0F59C434A7F457247DE7B",
    "55C50CE783C3CA76939EDA0FB5E6FF03",
    "BCD8EB77DAC23271AF208CD1D8F97A7E",
    "30696A950ACC6DBF6A928EF81559F057",
    "99295DB540C024D3FEAC4804C65A5845",
    "E85D7263AC6A0851DD1BF463D2277ABB",
    "85EFAE07DF4655F1317F68C3EDFCEE3A",
    "4C82D13A00B0ED6A392257A429AB24AD",
    "587A3298A2C315B2028136675969C238",
    "2734B2DFD3B658097D4C3B5ECE2C5249",
    "17FA7DF32D336766E3EABBA83B2DB32A",
    "6FF3D85EEFEDE0586E8BBFFA7D46BFAD",
    "5468F3C7F275D5E0B39F94411BF66577",
    "7548FC236DF20A4D2F8B751A7E94D561",
    "33046AB9D91DB644FFAC463D38EC48A3",
    "9D01599D44E820FB254A4C3CA2B8CD02",
    "4CB426C95610218316B6A79CE150A9A9",
    "BBE81347D3F23561E7D074C1408FFC1C",
    "1AB20CCBC0F2F9325FE56BE45F0AC534",
    "EB05C27BF7130B61AE34A5BB07DC589B",
    "850F75FE153C6F6BFBE1B35C1BFFFA61",
    "F9D780DEE11CB69B119148ADDAFD6832",
    "7A55ADC49C76F7E55146CA441912A123",
    "4B54A2ACC52CA8D10E84C50AFD109AD9",
    "E54A0F219DF49B4BBF89861857C607E2",
    "9250CA6C46490CF854101C82DB2F25B2",
    "D0DD544B86421849CD03C47B2CDAE4ED",
    "4A8214DCC6D2AFC97B8392FA71A3CE58",
    "92AF1495C61DAF007BC8923223D350BA",
    "A2A7143B194DEF58CC2B018210BA7A92",
    "9236714C118A6B3DFF30B70E3671230C",
    "D9D8B3E40FC657711F9B650A0AF61091",
    "65233C9E9338DAAFA3C1EAD15E7AC007",
    "FDCB39D62421803C764B2CE652AF6E23",
    "BCDCEB73DACE327D960C8CDDDC49448E",
    "7A866CFF80C499E63FB10B3F02C6814D",
    "55EA4D12882B864A101D2AACC95063C7",
    "DE8848A7789250C0842D2F61776B7023",
    "627B74817B658BF42DA3252D05170380",
    "5E2FC5C64491D1EF04254CB5EDC9D23B",
    "65B93C0393A7DA12A37BEA6BAC4004B1",
    "1DCE74F2CBD49203DB6AA27487147BDB",
    "832EEEDB9F1B968E718228B06BA86CA8",
    "D5DE01C30C329801CC1814DBD0E79082",
    "3CAB5E39CE7846AFC2AD9891FED8DDD3",
    "53B0F49FCBAACC1914DB93B9D0040757",
    "67067F7E73648E76282122A86CE61978",
    "EA635CCE6C7C64EF25EA3B4AB411B08C",
    "F3FEA804CB5EAF4DA9FCEC0B9381C713",
    "A073EEEE9F2C969B719128ADC2FD8BBB",
    "8B63110AB7DDE524D161987180CC42C0",
    "7FFEA8519FE0F0539196CFFFEAA703E3",
    "5FFF5705D2E0BC7F1A2E30A142700825",
    "E3FDCE8FBFCFF67A51F6084B54E181B3",
    "34BC6EC10E18698B6EBE06F43C17CABC",
    "C1F535E8381F8CEE2F77203727688F60",
    "C496F2D19311EAB87DB4348A49801CE5",
    "573482AA8EDD1DA8EA52977191388B58",
    "B52961B56CC0F8D3C58A7404FA4D8723",
    "228B7B35D6919FC7E429ADB97F27B1C2",
    "9BD0F02EE374D727C11A25B90ACC413D",
    "F9133D8F20E684F569CC282EB41C8ED0",
    "15489EC45FCADEC10A8B02F27D491174",
    "9A64B0BB6133CAEA1EA23624C58BC409",
    "A9FCE3C05FEA296D71873F16135DE00E",
    "889C3EB30E8E08CCFB8D576DA72AF867",
    "4B098E95B2E009F3B4FE9B2485B4B96E",
    "6D01DA2FE91AE249CF08BDE9CF6D2D70",
    "BE17D56B84B6F4E5E457355A96CF4325",
    "685ADFF5EE47E1F6BADFB853A9EABE1D",
    "FF33D18E6D287BAF43C109D10C10D644",
    "C289341539638F729A0E21A4A3A9DDBF",
    "0DB93E776EB726E1A26FF8D3AC3C7AD8",
    "79E750D9EFFDF654BFBC862D57442919",
    "C38C6966FF31BD8099C4E0D612B9CC0E",
    "97038E79278D4763D23AE9B5E6CC8E5E",
    "93295D5BCD9B470EC3039B3F418E42FF",
    "AE079D3A8E7B87AE02A25B907D8B7643",
    "2060795CD47999E8E600AF92156B180A",
    "2F09EA9596E075F38D2EFF2491B8988C",
    "4349B655BAA001B39431A3646EBF4326",
    "CE4627BE524E2CA78B714078BFA8B4A1",
    "77312E8CE52EE899B1F3F8E3E63FAE30",
    "A79E29D55915D384B788EFB69028183C",
    "C5F2615D41ECBB5F0FC406FB4B0BD799",
    "B984236EA139C188F5CCBCDE9F5BA982",
    "921D8961E8B8C0EBC8594EE4ADCE863F",
    "10279C8C5D02263902F31A0BD715FB83",
    "85C5FE399163D912DF21919735146700",
    "C7BA679547A4B917F3A100B34768D4E0",
    "6EACDAAB1B239AEA4EA246244D7817A1",
    "77D72F2B4F712A242D17211AB0F9A47B",
    "C6829E3E3298B8CE002648B06ED59286",
    "E7FE475167E0595364BA20FFE6CC07B4",
    "81FF7245AC4C0877DD39F441C4BFF30C",
    "90AA42384F4EDD5DFEDE5787EA0D86DA",
    "EC7A26682B9FB16DF5C033B7793284CF",
    "C569A4907516FE0D2AC7223F9410A41A",
    "DE45B5B925E0949384A634706D385549",
    "1DD4792A197050234716E815920AD839",
    "DE4E4425C4F0514F8485CD14921AC387",
    "32636B5D2778AFEFF401BD91CB2AF5E6",
    "CC4B7739A7B10F94D85DF1A520E8E8A2",
    "E3844BAB7B865D3567472C9523BF67FC",
    "7FFB7701DC349C7B3A3210BDCE04817B",
    "C4539A518B91823805355C09EF5FCA5F",
    "E85CA0601C4566FC2E14768681754737",
    "1BA37FC9BFC107E4E0ACF9D5E4A4EEFE",
    "0DCBBA6689D5820016C1DDA2FD5BF3F1",
    "6F9C26209D8AE03DA954F046474AB62E",
    "AFC4E1F85DC22175699F370EA50D9306",
    "B12E65B468C3FCD29615700B8FEB3151",
    "AA4083B8DB6048ADEF7BE476BF30FD77",
    "EC85562587AD6F90B859D1A160E27BE1",
    "A297BBEE0BE05017E7C6DCC92660E7A5",
    "94298F55EE8CC4F3B4417E0C3E3C8919",
    "63FD7B0396EB906526301CBF345DE7D7",
    "58053279A2A015D30261A3688C6C5B9B",
    "D7B3890D05A9491811715F612869BE0B",
    "908889F1480E4214D5C3EECE4CE0936B",
    "AE9987E0615E4C05EBD0E0DFF37F51E5",
    "B1903B7AA92DCFB4EBF0B2E24D62EE25",
    "DD9DB4906516CE0D1AC7323F641C335D",
    "F29EA9E3C83EA06DA8DC428759B10DAC",
    "024DF938AA79E3A066AC3F9286D25BD4",
    "E33C4B127B215D9C883A2C3D678FCEF5",
    "387D914F2D6AB1DDFE3747A74A773A1F",
    "199D8077012E608155C713D75FB2A1D3",
    "120131AD51ED2B5CBFD0F76D3C04973D",
    "46191FA4B20638B180DBC9CB295E34A8",
    "A1DA15C7183EEC0DFABC00D79057F0CF",
    "B8C2EF6DDEDC360F497588ABA103F5EC",
    "524144B76A6081AE17782377C9828058",
    "86DA2CB1BC67FAFADC3EA5A8B8C267E3",
    "B8AF1111ACB5362C7E45C7557C267B7F",
    "64617E97C37397CE21991917513F3FE2",
    "A1D3057E25CD1F783D3B62DA4ABB40CF",
    "D48ACDF376B406EA91BDAACC4329271A",
    "7E80BB1EA568027B816EAEBD8F1C7B13",
    "F7757D20E3F7894AAD8EF41F67DD4958",
    "347E6E840EDF69CE6E7C8845AA3E5FD3",
    "8BA1114BB71AE565D1A3983226570212",
    "CFFB81C53DE1415009B85729DC5DEAF5",
    "C8E3528AF25CB2B3A4F1EDE1AE1A3FD0",
    "B1C81567D5D22F01062172A1170D837D",
    "04A77EDA1E0159745EC73E7A03CECBAA",
    "547D816183941866A97094B8B051EB9C",
    "2B72B619D7CC445371913F00FFD1C674",
    "46EDED887C5E39A11CE764F73EC105BB",
    "610038BD9719DE48A7A0EE311C56A403",
    "9725C9984522099551FF1FEF446FADEF",
    "7C8C16F14628315B26EEA22F0B763516",
    "0F46E6D387139E86098A20880FE59DD8",
    "FFC8F630F0930924A0F39BFE4150BAB7",
    "4C8D26F0562B215A16E97DD23A5D9143",
    "FBEA77E8A7DE0FC5D88FF1F6397CBF46",
    "3D801400C686AFBD7B74928E79B39EFE",
    "37CF5A65846C6057C519DC61692AB87D",
    "3864529A02C175B4628770B9FA8EFE4C",
    "92B589C8E813C082C8B1DBF5EA3EC2F6",
    "51DD84C088370916B28D9BC89BC7C8CC",
    "7FFBBAE6A61105EC6749AF354BB8438E",
    "FA0DB5406449C17C2534334E0AA5843E",
    "4BA1FB4F3A46837D67377D4FA7C8F866",
    "6D60F40B15DA022537607D72A0471E26",
    "0315AE003FD77C2A596F277F427F6A11",
    "E8735EDE6E6C66DFB624397A44D10433",
    "CEC06B401BFE6B39FF34B70AB4B606B3",
    "C9E183DB3FFF476A0F8255131C177546",
    "FA77F38DA42918F0BFA79429F9D55253",
    "89524D5070A7D4B67F18586F81FC0BED",
    "6F5CB4BD6535CEE81AA032D9B2615556",
    "2829024F209BCBB66D60656F6DCD5F44",
    "5150CAAEADF50CA80B9B70028E24D3BC",
    "FE1A18A3DA2BA31287DA9E2C9364F051",
    "401D19A0B40A3EBD86D7CFC74754D57B",
    "7EB2BB30A546025569A4AE8F5EC5FCFD",
    "FAB33C2F215987544FC6298E60DD61DA",
    "A25004FF244D1CF86EF3635943AF60C7",
    "B963EECEDD7C37EFBE46894AFF4EFF49",
    "F931D38C6F2E77993FF305E365C81BCE",
    "104B0AB18AD5C3D455836D0D1FE9B5A4",
    "0A87CF1BF16D40481B28EC92C9562EB8",
    "BB3A5944C9824335C7389F0671C17C3D",
    "7A8BADA69C95F7C70FA6CA625D5AE97D",
    "92E3B920EA61A3C826447FFAE23AA3EB",
    "4BAF0211B1B5C42C8D45D455634DF50C",
    "73092AB49916EC41B5ABFC3A1106FF06",
    "09D740E9FFCD8664CF8C961D530D425D",
    "81CDFA319D6BDD1ADB297E484470D55C",
    "D287041B096D9F78CACA11A2F53992A0",
    "270F496D39AD731CD7118F2D23E9CE22",
    "24935EEE3E3579687EDB3D8EBE2A3E01",
    "AB216FBD12C8E0AB456E0C0CC90C4758",
    "73E86B10F2CFE07436230CAE7AF9221E",
    "6DDCA8C155342D176A7747C966BF6A62",
    "190803B3D33B5BE28CAA85D396A4839B",
    "81E9254005F37F62F69142C03396C59D",
    "D3143108E1FE47B5A07CB98691D539E4",
    "BC33D6EEB72CCE9B599110ADE6A8F5F4",
    "33A69489ABB8AC2B98CFF3B77A138457",
    "56F0DD9B4C4D29D40C105482F430CD28",
    "4BF302CDB1E9C4588DB0D42102BC392A",
    "FC81E29983D99A400DCC2471FFBE9AEB",
    "DE9DB5E0253B946A84D99C8E36888685",
    "C5D431C93C3C880F151E24D187C74537",
    "0D79941435C3625E579A1D0B6FABF370",
    "4B14FC3AC309C4A4D8279B052B23B5BB",
    "B64FEE71A254288370E538F50B9072DB",
    "E06346CE667C5EEF1F30214AA610625B",
    "D12E8B9307374FA217CA5DD4DBB2CB78",
    "A118158618F1ECCC5DF90015013E2B5C",
    "7E8F5731EA95F3C3B82581B5FBE47998",
    "2CC917AB77EB072E8323DB1F1D43EE7F",
    "2C75068B1F6FCFF269A5612BE1EECE97",
    "7B48BE56A2A139BCA81AAB65B6BF9157",
    "91E445F9480CDC1F577650C1BCB64A06",
    "BC55D7A986F0ECB3EC868510AD962760",
    "3345E659EAAC71BFE36DF36059497E07",
    "5B9A32268180D4379D5EE4485A672154",
    "A49F4F2DAFA51798D051C9A9C093B7C4",
    "3306BEED2FB84C076942376C7D5A8B7B",
    "1E6E7752CA7793E2D80AA1949380EE05",
    "F010E968C942629DB54B8E4650B43F48",
    "CAB80C2631508133869823E5956FE0EC",
    "161B08619EFCC58453526F5D7E511BF0",
    "0AA43C5CFE554648A300BA7A9DEB7775",
    "BCA7EB8ADAB93214463E8CB6C13D866A",
    "025AA99CDADA524D36C36F7E202398F5",
    "53D24B2AE1D1805216052C8432B09AF1",
    "C5999F233387BB32035B494B04B412FE",
    "FDFB39E6241180EC84EB2C354DEFD3FD",
    "BD7D2718A5CFF352E796AE0764ED7F27",
    "DA0FB17321AE88DD806FA282DD0306A8",
    "D1269662F7A08E17191A5038D078061D",
    "CA08A6B17739F6FC32B42ACD7FBC10C7",
    "34521326C3ACA266862E9F5039D9CE14",
    "997607A5D72D5F1088D881222B8FD1C1",
    "37DD6F210F7B6A2A6D199EE074EBA1B0",
    "127A04827068C1FB57B2633C4E23794F",
    "9F30F44EE795D307C53A0B3DFE8F7AC3",
    "389F52E20239756C62DF6ACAB5EADF4C",
    "1DB2740ECBA8921FDB76A260C7996771",
    "ABA5FD0751A325166D7F2B6FE621F74F",
    "E35A55EF352F4F9ADB9693AC308DC51E",
    "97881D628335E98CCDC894DA6B0CA5CC",
    "F1137BFAE9AD8F34AB71F2618E8D896F",
    "4CBD26C0561B218A16B9008B251D8B95",
    "4B3D0280B12AC49D8DF7D4E77A11A06A",
    "FADA530A83806BBBBC72D594EBBD97CF",
    "C7A1AD4FDE8F563A32376B0B5A0132FF",
    "B2DC38B7A861CEF0E834B1A642DEC93B",
    "E787B939159D5934215D6F4D5D2D6837",
    "FB241CC0DEC6A7FD83B79ACEA2AE0058",
    "67B9F2531302189D3DDB7BCBC368F413",
    "1E4010B86CA2FDAD5B7B777664ADF454",
    "C0586720B7A63F9DE854E1AE1B11280E",
    "EA3142779C7E1825CDEFC41740EE3368",
    "34986EE50E3C696F6EE2FC712B2763AD",
    "4ED8D5B3746521FC14385CAAECB27440",
    "131E9EF50FA06C3F497A176455ABAF45",
    "DDFBB607D95D91308703F36E54F19288",
    "7954E03F6116366923AF693E3B4EE7BD",
    "8BDEE024937EE72DD11CFBC35E262A31",
    "5FEC9AF186046517932E8FC9E3A89FEF",
    "418363BAB3303BEBECDDE525F2D623D2",
    "2F7CBA172BCE405175973306D56B0B78",
    "2737B2DED38958087D4D3B5DD683293B",
    "4DEFFA42C9F1C26CB16A9DCE2A41C59D",
    "5E472D6F5DAFD71AB317EB2B5FB20F01",
    "E691FFE81C36141DA3C898C73F6F2653",
    "E1700B1B99CA9F55BB938202DB1F6F5E",
    "4E768B6CB59B126930049EB3F433E940",
    "2DCF053599A6CE2F68FE62F14E6105CB",
    "8DCC49D17424D03705425CE9A04614F8",
    "D4558C5700724AE5120F5A9FD6A27F36",
    "25CE4134316E781D7F2C236D86A4C6A9",
    "2E23F7059044EDF3787931C5C8A35D75",
    "D77C4C822CD985DC726EE681E2238E81",
    "97881D628335E98CCDC894DA6B0CA5CC",
    "28BD58EFC82F5E6ACAE6635B66C60FC8",
    "6774F21F13F618493D8F7B1E2E75CC3E",
    "82D928B4B862FEFDD83BA1ABB922780C",
    "13B95C5C9E556648C300DA7A3DD41704",
    "C395F8EB39E382DA66927EEB42D849B0",
    "A013B969668E529CE54ADE45DB1ACD3B",
    "FDB0D70C6BAE73193B7001623F1A0946",
    "CA72516A81636D5ABE13D06B907C0B23",
    "DE15B56925B094E38451EB2FA4F9909D",
    "8F09EB41CA48B37377356D4D3013717D",
    "5B5853E133214398C7949FAAEB41F848",
    "B9697D756080C493E56F6844A54FA811",
    "25CD7CFFD3DBAC1EF577BC67EB2752E4",
    "E5C8FC305D630954A0039B8E94B3DEA3",
    "9514313A31091DB40E2C6C15594AD801",
    "81D5DBD777F37F66478E0D1F0C5649AE",
    "844822E702557A801A434521621905B6",
    "F0A96C061C4768F2FC7EAAC4E129C442",
    "8C72E58A85946EF3C9AA82247ED44AF2",
    "33266B5C0B8758055F349A438D9C9B05",
    "473D3F415F981A0A1D396B50050D9A3D",
    "84844E1A736CC97FE51A5BA1BBD45C4D",
    "D79B5D71C324A9BB8DF9D4E9428F7094",
    "3CD9A7B4266273FD663B2EABDB2BD1AA",
    "A9301D1E2D2D279805CB7A39227FE993",
    "6AAF7CD6AECC890F2FDE1BD15D3B9F92",
    "98A955A735E74F52DBDE9363ED0F2AAD",
    "89103D3E0D0D07B8BB7B5A1997EBC297",
    "EC1EC56679F80E9FA949A240D39ED9AF",
    "D81CB36223B980FC884ECB6D2F977A79",
    "EEF97494944282DDB41BFD8BB7ECDDC2",
    "ACCA1A652AD43417186F8AB37C14934F",
    "64661E9C7EC739B63E85F99DF5AD29A8",
    "24685E963ECD79A07E93BF25F14EA1AE",
    "DC839B615A68235307151D6D15EF67B6",
    "4F248ABAB6CD15D88F419F0123EBDA5D",
    "2F2A6697DD33A0A6E9CEB0D8FB50F4AE",
    "D2AB043709419F5C5B2611862768FDF1"
]


@app.route("/GetRespString", methods=['POST'])
def GetRespString():
    try:
        id = int(request.form['id'])
        return resp_array[id]
    except:
        return ""


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0", debug=True)

#finalize()