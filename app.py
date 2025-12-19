# 웹페이지를 만들기 위한 도구를 불러오기
# pip install flask reportlab
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import webbrowser

# Flask라는 웹앱을 만들기
app = Flask(__name__)
app.secret_key = "haeun-2025-secret" # 세션 정보를 안전하게 관리하기 위한 비밀 키 설정하기

# 문항번호들 저장하기
# A, B, C, D, E는 연습 문항, 1부터 185까지는 본 검사 문항
LABELS = ['A', 'B', 'C', 'D', 'E'] + list(range(1, 186))

# 수용 어휘 문항번호, 문항 내용, 정답 저장하기
ALL_ITEMS = [
    ('A', '사과', 1), ('B', '다리', 4), ('C', '책', 2), ('D', '가위', 2), ('E', '연필', 4),
    (1, '바퀴', 3), (2, '주전자', 3), (3, '소', 4), (4, '사다리', 1), (5, '시끄럽다/시끄러운', 4),
    (6, '발톱', 1), (7, '요리사', 2), (8, '바르다', 3), (9, '설거지하다', 2), (10, '접시', 3),
    (11, '신다', 2), (12, '소방관', 3), (13, '뚜껑', 3), (14, '놀라다', 3), (15, '국자', 2),
    (16, '혀', 2), (17, '넥타이', 2), (18, '점', 1), (19, '잠자리채', 4), (20, '당기다', 3),
    (21, '연기', 1), (22, '찢다', 3), (23, '피리', 3), (24, '던지다', 2), (25, '무릎', 2),
    (26, '풀', 2), (27, '구르다', 1), (28, '뱉다', 3), (29, '파괴하다', 3), (30, '윷', 3),
    (31, '팔꿈치', 2), (32, '재다', 2), (33, '따르다', 1), (34, '삽', 2), (35, '기둥', 4),
    (36, '채소', 1), (37, '따뜻하다/따뜻한', 2), (38, '묶다', 3), (39, '망원경', 4), (40, '격파하다', 3),
    (41, '가득하다/가득한', 1), (42, '깍다', 3), (43, '농부', 1), (44, '곡식', 1), (45, '마르다/마른', 1),
    (46, '실망하다/실망스럽다', 3), (47, '쓰다듬다', 4), (48, '외투', 3), (49, '철봉', 2), (50, '궁궐', 4),
    (51, '씹다', 2), (52, '숲', 4), (53, '집배원', 4), (54, '둥지', 4), (55, '겨루다', 4),
    (56, '한권', 3), (57, '소근거리다', 1), (58, '엿보다', 4), (59, '환자', 3), (60, '심다', 4),
    (61, '체온계', 1), (62, '만국기', 1), (63, '책상', 3), (64, '세면대', 3), (65, '전등불', 3),
    (66, '돛', 1), (67, '협동하다', 4), (68, '위급하다/위급한', 2), (69, '정육점', 3), (70, '얼룩', 4),
    (71, '탄광', 2), (72, '석수', 3), (73, '식료품', 1), (74, '뿌리', 4), (75, '확대하다', 2),
    (76, '자매', 4), (77, '부축하다', 3), (78, '해안', 1), (79, '연장', 1), (80, '도표', 2),
    (81, '해부하다', 1), (82, '굽이치다', 3), (83, '토론하다', 2), (84, '버드나무', 2), (85, '부화하다', 1),
    (86, '설계사', 3), (87, '비석', 4), (88, '추수하다', 3), (89, '한쌍', 1), (90, '가축', 4),
    (91, '각도기', 4), (92, '조명', 2), (93, '침몰하다', 2), (94, '방충망', 1), (95, '대여섯', 1),
    (96, '늠름하다/늠름한', 2), (97, '철거하다', 2), (98, '시위하다', 3), (99, '기마전', 2), (100, '에워싸다', 1),
    (101, '산만하다/산만한', 1), (102, '용접하다', 4), (103, '접종하다', 1), (104, '장착하다', 3), (105, '섬기다', 4),
    (106, '겨누다', 2), (107, '육군', 4), (108, '소음', 1), (109, '침울하다/침울한', 2), (110, '폭우', 3),
    (111, '후각', 1), (112, '모발', 2), (113, '사육하다', 3), (114, '건널목', 3), (115, '현상', 1),
    (116, '시시덕거리다', 2), (117, '업신여기다', 2), (118, '부식되다/부식된', 2), (119, '산호', 4), (120, '땀샘', 3),
    (121, '비집다', 2), (122, '빈궁하다/빈궁한', 4), (123, '야위다/야윈', 3), (124, '거구', 4), (125, '낭독하다', 4),
    (126, '궤짝', 4), (127, '고삐', 2), (128, '모과', 2), (129, '답사하다', 3), (130, '타박상', 4),
    (131, '우뢰', 3), (132, '관현악', 2), (133, '중추', 3), (134, '축산물', 1), (135, '원예', 1),
    (136, '노쇠하다/노쇠한', 3), (137, '쌀겨', 4), (138, '지혈하다', 1), (139, '광야', 1), (140, '만발하다', 3),
    (141, '청중', 2), (142, '피복선', 3), (143, '게스츠레하다/게슴츠레', 4), (144, '질책하다', 3), (145, '묘목', 2),
    (146, '그을리다/그을린', 2), (147, '기슭', 1), (148, '신봉하다', 3), (149, '파종하다', 4), (150, '박멸하다', 1),
    (151, '미닫이', 4), (152, '군의관', 2), (153, '굽다/굽은', 1), (154, '강탈하다', 4), (155, '종사하다', 3),
    (156, '가무', 1), (157, '번뇌하다', 2), (158, '매몰되다', 1), (159, '방적하다', 3), (160, '절경', 3),
    (161, '영장류', 3), (162, '성기다/성긴', 1), (163, '외향적', 3), (164, '조정하다', 3), (165, '유전', 4),
    (166, '사색하다', 2), (167, '피뢰침', 4), (168, '긍휼', 2), (169, '맹금류', 1), (170, '주검', 1),
    (171, '검열하다', 1), (172, '용해시키다', 1), (173, '과적', 1), (174, '잉태하다', 4), (175, '상쇄하다', 2),
    (176, '투항하다', 2), (177, '편종', 4), (178, '봉화', 3), (179, '도정하다', 1), (180, '반추하다', 1),
    (181, '탈고하다', 3), (182, '산적하다', 1), (183, '산재하다/산재한', 2), (184, '다사롭다', 3), (185, '독특하다/독특한', 1)
]

# 나이에 따라 검사 시작 위치 정하기
# 수용 어휘 검사만 실시하는 경우 표현 어휘 검사의 시작 문항을 따른다
def get_start_index(age):
    if 2 <= age <= 4: # 2~4세: 1번
        return LABELS.index(1)
    elif 5 <= age <= 6: # 5~6세: 16번
        return LABELS.index(16)
    elif 7 <= age <= 9: # 7~9세: 46번
        return LABELS.index(46)
    elif 10 <= age <= 12: # 10~12세: 91번
        return LABELS.index(91)
    else: # 13세 이상: 121번
        return LABELS.index(121)

# 검사 시작 페이지 만들기
@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        age = int(request.form.get("age")) # 나이 입력값 받기

        # 검사 전에 필요한 정보 저장하기
        session.clear()
        session.update({
            'age': age,
            'items': [], # 검사 반응을 담을 리스트 만들기
            'base_found': False, # 기초선을 찾았는지 표시하기
            'base_index': None,
            'complete': False,
            'pre_items': ['A', 'B', 'C'] if age < 6 else ['D', 'E'], # 연습 문항 정하기 (6세 미만은 A, B, C만, 6세 이상은 D, E만)
            'start_index': get_start_index(age), # 시작 위치 저장하기
            'mode': "practice" # 연습 문항으로 시작하기
        })
        return redirect(url_for("index"))
    return render_template("start.html")

# 실제 검사 화면 보여주기
@app.route("/", methods=["GET", "POST"])
def index():
    # 검사 정보가 없으면 처음으로 되돌아가기
    for key in ['items', 'mode', 'pre_items', 'start_index']:
        if key not in session:
            return redirect(url_for("start"))

    items = session['items']
    mode = session['mode']
    current_index = len(items)
    result = ""

    if request.method == "POST":
        item = request.form.get("item") # '+' 또는 '-' 받기

        if item in ['+', '-']:
            items.append(item)
            session['items'] = items

            # 연습 문항을 다 풀었을 경우 검사 시작 또는 종료 결정하기
            if mode == "practice" and len(items) == len(session['pre_items']):
                if all(i == '+' for i in items): # 모두 맞으면 본 검사로 넘어가기
                    session['mode'] = "main"
                    session['items'] = []
                    return redirect(url_for("index"))
                else: # 하나라도 틀리면 검사 종료하기
                    session['complete'] = True
                    return render_template("form_step.html",
                        current_label="종료", target_word="",
                        responses=items, result="❌ 연습 문항 실패로 종료되었습니다.",
                        complete=True, base_found=False, base_index=None)

            # 본 검사를 진행 중일 때 처리하기
            elif mode == "main":
                if session['start_index'] + current_index >= len(LABELS):
                    session['complete'] = True
                    return redirect(url_for("report"))

                # 최근 8개의 반응 확인하기
                last_8 = items[-8:]
                plus_count = last_8.count('+') # 맞은 개수 세기
                minus_count = last_8.count('-') # 틀린 개수 세기
                label_now = LABELS[session['start_index'] + current_index]

                # 기초선 조건을 만족했는지 확인하고 저장하기
                # 기초선: 연속해서 8개 문항을 맞추는 경우
                if not session['base_found'] and plus_count == 8:
                    session['base_found'] = True
                    session['base_index'] = label_now

                # 최고 한계선 도달 시 검사 종료하기
                # 최고 한계선: 연속된 8개 문항 중에서 6개를 틀리는 경우
                if minus_count >= 6:
                    session['complete'] = True
                    return redirect(url_for("report"))

    current_index = len(session['items'])

    # 지금 보여줄 문항 정하기
    if session['mode'] == "practice":
        if current_index >= len(session['pre_items']):
            return redirect(url_for("index"))
        current_label = session['pre_items'][current_index]
    else:
        if session['start_index'] + current_index >= len(LABELS):
            return redirect(url_for("report"))
        current_label = LABELS[session['start_index'] + current_index]

    # 문항번호에 해당하는 단어와 정답 찾기
    item_dict = dict((k, (v, a)) for k, v, a in ALL_ITEMS)
    target_word, target_answer = item_dict.get(current_label, ("", ""))

    return render_template("form_step.html",
        current_label=current_label,
        target_word=target_word,
        target_answer=target_answer,
        responses=session['items'],
        result=result,
        complete=session.get('complete', False),
        base_found=session.get('base_found', False),
        base_index=session.get('base_index'))

# 오답 문항만 보여주는 결과 페이지 만들기
@app.route("/report")
def report():
    responses = session.get("items", [])
    mode = session.get("mode", "practice")
    pre_items = session.get("pre_items", [])
    start_index = session.get("start_index", 0)

    labels = pre_items if mode == "practice" else LABELS[start_index : start_index + len(responses)]
    wrong_items = []

    for i, r in enumerate(responses):
        if r == '-':
            label = labels[i]
            word = dict((k, v) for k, v, _ in ALL_ITEMS).get(label, "")
            wrong_items.append((label, word))

    # 기초선/최고한계선 정보 찾기
    base_index = session.get("base_index")
    limit_index = None
    base_word = None
    limit_word = None

    # 기초선 문항 내용
    if base_index is not None:
        base_word = dict((k, v) for k, v, _ in ALL_ITEMS).get(base_index, "")

    # 최고한계선: 마지막 문항 번호
    if responses:
        limit_index = labels[-1]
        limit_word = dict((k, v) for k, v, _ in ALL_ITEMS).get(limit_index, "")

    return render_template(
        "report.html",
        wrong_items=wrong_items,
        base_index=base_index,
        base_word=base_word,
        limit_index=limit_index,
        limit_word=limit_word
    )

# 검사 결과를 PDF로 저장해서 다운로드하게 만들기
@app.route("/download_report")
def download_report():
    try:
        import os
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        FONT_PATH = os.path.join(BASE_DIR, "static", "fonts", "malgun.ttf")

        # PDF에서 사용할 글꼴 등록하기
        pdfmetrics.registerFont(TTFont("Malgun", FONT_PATH))
        buffer = BytesIO()

        # 페이지 아래쪽에 안내 문구 넣기
        def footer(canvas, doc):
            canvas.saveState()
            canvas.setFont("Malgun", 9)
            note_text = (
                "※ 수용 어휘 검사만 실시하는 경우 표현 어휘 검사의 시작문항을 따른다.\n"
                "2~4세: 1번, 5~6세: 16번, 7~9세: 46번, 10~12세: 91번, 13세 이상: 121번"
            )
            text_obj = canvas.beginText(40, 18)
            for line in note_text.split('\n'):
                text_obj.textLine(line)
            canvas.drawText(text_obj)
            canvas.restoreState()

        # PDF 문서 틀 만들기
        doc = BaseDocTemplate(buffer, pagesize=A4)
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='with_footer', frames=frame, onPage=footer)
        doc.addPageTemplates([template])

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Malgun', fontName='Malgun', fontSize=9, leading=11))

        responses = session.get("items", [])
        mode = session.get("mode", "practice")
        pre_items = session.get("pre_items", [])
        start_index = session.get("start_index", 0)

        labels = pre_items if mode == "practice" else LABELS[start_index : start_index + len(responses)]
        response_marks = {str(labels[i]): '+' if r == '+' else '-' for i, r in enumerate(responses)}

        start_label = str(LABELS[start_index])
        base_index = str(session.get("base_index", ""))
        last_label = str(LABELS[start_index + len(responses) - 1]) if responses else ""

        wrong_items = []
        for i, r in enumerate(responses):
            if r == '-':
                label = labels[i]
                word = dict((k, v) for k, v, _ in ALL_ITEMS).get(label, "")
                wrong_items.append((label, word))

        elements = []

        # 오답 문항 먼저 보여주기
        if wrong_items:
            wrong_summary = "<br/>".join([f"{label}번: {word}" for label, word in wrong_items])
            elements.append(Paragraph("오답 문항<br/>" + wrong_summary, styles["Malgun"]))
            elements.append(Paragraph("<br/><br/>", styles["Malgun"]))

        # 모든 문항을 표로 정리해서 보여주기
        data = [("문항번호", "문항내용", "정답", "반응(+, -)")]

        for label, word, answer in ALL_ITEMS:
            label_str = str(label)
            annotations = []

            if label_str == start_label:
                annotations.append("시작번호")
            if label_str == base_index:
                annotations.append("기초선")
            if label_str == last_label:
                annotations.append("최고한계선")

            if annotations:
                tag = "<br/><font color='green'>" + ", ".join(annotations) + "</font>"
                label_cell = Paragraph(label_str + tag, styles['Malgun'])
            else:
                label_cell = Paragraph(label_str, styles['Malgun'])

            mark = response_marks.get(label_str, "")
            data.append((label_cell, word, str(answer), mark))

        # 표 스타일 설정하고 PDF에 넣기
        table = Table(data, colWidths=[60, 200, 40, 60], repeatRows=1)
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Malgun'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))

        elements.append(table)
        elements.append(Paragraph("<br/><br/>", styles["Malgun"]))

        # PDF 파일 만들기
        doc.build(elements)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True,
                        download_name="검사결과지.pdf", mimetype="application/pdf")
    
    except Exception as e:
        print("PDF 생성 오류:", e)
        return f"PDF 생성 중 오류 발생: {e}", 500

# 실수했을 때 마지막 문항 지우기
@app.route("/undo", methods=["POST"])
def undo_last_item():
    if 'items' in session and session['items']:
        session['items'].pop()
        session['base_found'] = False
        session['base_index'] = None
        session['complete'] = False
    return redirect(url_for("index"))

# 처음부터 다시 검사 시작하기
@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("start"))

# 웹서버 실행하기
if __name__ == "__main__":
    # app.run(debug=True)
    webbrowser.open("http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000)