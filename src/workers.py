import langdetect
DEMO_POEM_SRC = """
Zwei Straßen gingen ab im gelben Wald,
Und leider konnte ich nicht beide reisen,
Da ich nur einer war; ich stand noch lang
Und sah noch nach, so weit es ging, der einen
Bis sie im Unterholz verschwand;
""".strip()

DEMO_POEM_REF = """
Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;
""".strip()

DEMO_POEM_HYP = """
Two reads went the other way in a yellow wood
and sorry I could not go both ways
and since alone I was, I stood for long
and examined how far one of them went
until it disappeared in the bushes;
""".strip()

DEMO_METER_SRC = [4, 4, 4, 4, 4]
DEMO_MDESC_SRC = "fixed pentameter, iambic"
DEMO_MDESC_REF = "fixed pentameter, iambic"
DEMO_MDESC_HYP = "hexameter + pentameter, iambic (irregular)"
DEMO_RHYME_SRC = "ABAAB"
DEMO_RHYME_REF = "ABAAB"
DEMO_RHYME_HYP = "ABABC"

LABEL_SRC_REF = "Source & Reference"
LABEL_SRC = "Source"
LABEL_REF = "Reference"

EVAL_DUMMY = {
    "meter_sim": float("-inf"),
    "line_sim": float("-inf"),
    "meter_xxx": float("-inf"),
    "meter_hyp": float("-inf"),
}


def translate_poem(poem):
    return DEMO_POEM_HYP


def meter_regularity(meter):
    """
    Output is bounded [0, 1]
    """
    score = 0
    for i in range(1, len(meter)):
        if meter[i-1] == meter[i]:
            score += 2
        elif abs(meter[i-1]-meter[i]) < 1:
            score += 1
    return score/(max(len(meter)-1, 1))/2


def meter_regularity_sim(reg_1, reg_2):
    """
    Output is bounded [0, 1]
    """
    return 1-abs(reg_1 - reg_2)


def line_count_sim(count_1, count_2):
    """
    Output is bounded [0, 1]
    """
    return min(count_1, count_2)/max(count_1, count_2)


def evaluate_vs_hyp(poem, poem_hyp):
    # stress_count = [[px.meterVal for px in p.positions] for p in parsed.bestParses()]
    # print(stress_count)
    import prosodic

    if poem == DEMO_POEM_SRC:
        # debug todo
        regularity_xxx = meter_regularity(DEMO_METER_SRC)
        meter_xxx = ", ".join([str(x) for x in DEMO_METER_SRC])
    else:
        parsed_xxx = prosodic.Text(poem, lang="en", printout=False)
        parsed_xxx.parse()
        meter_xxx = [p.str_meter().count("s") for p in parsed_xxx.bestParses()]
        regularity_xxx = meter_regularity(meter_xxx)
        meter_xxx = ", ".join([str(x) for x in meter_xxx])

    # TODO: this computation is duplicated
    parsed_hyp = prosodic.Text(poem_hyp, lang="en", printout=False)
    parsed_hyp.parse()
    meter_hyp = [p.str_meter().count("s") for p in parsed_hyp.bestParses()]
    regularity_hyp = meter_regularity(meter_hyp)
    meter_hyp = ", ".join([str(x) for x in meter_hyp])

    meter_sim = meter_regularity_sim(regularity_xxx, regularity_hyp)
    line_sim = line_count_sim(poem.count("\n")+1, poem_hyp.count("\n")+1)

    return {
        "meter_sim": meter_sim,
        "line_sim": line_sim,
        "meter_xxx": meter_xxx,
        "meter_hyp": meter_hyp,
    }


def evaluate_translation(radio_choice, poem_src, poem_ref, poem_hyp):
    log_str = []

    try:
        lang_src = langdetect.detect(poem_src)
    except:
        log_str.append("Unable to recognize src language")
        lang_src = "unk"

    try:
        lang_ref = langdetect.detect(poem_ref)
    except:
        log_str.append("Unable to recognize ref language")
        lang_ref = "unk"

    try:
        lang_hyp = langdetect.detect(poem_hyp)
    except:
        log_str.append("Unable to recognize hyp language")
        lang_hyp = "unk"

    log_str.append(
        f"Recognized languages: {lang_src} -> {lang_ref} & {lang_hyp}")

    if lang_ref != lang_hyp:
        log_str.append(
            "WARNING: Reference and translate version languages do not match")
    if lang_src == lang_ref:
        log_str.append(
            "WARNING: Source and reference version languages are the same (not a translation)")
    if lang_src == lang_hyp:
        log_str.append(
            "WARNING: Source and translated version languages are the same (not a translation)")

    if radio_choice == LABEL_SRC_REF:
        eval_src = evaluate_vs_hyp(poem_src, poem_hyp)
        eval_ref = evaluate_vs_hyp(poem_ref, poem_hyp)
    elif radio_choice == LABEL_SRC:
        eval_src = evaluate_vs_hyp(poem_src, poem_hyp)
        eval_ref = EVAL_DUMMY
    elif radio_choice == LABEL_REF:
        eval_ref = evaluate_vs_hyp(poem_ref, poem_hyp)
        eval_src = EVAL_DUMMY

    meter_sim_best = max(eval_src["meter_sim"], eval_ref["meter_sim"])
    line_sim_best = max(eval_src["line_sim"], eval_ref["line_sim"])

    score = 0.9 * meter_sim_best + 0.1 * line_sim_best
    return (
        f"{score:.3f}",
        [
            ["Meter similarity", 0.9, meter_sim_best, 0.9 * meter_sim_best],
            ["Line similarity", 0.1, line_sim_best, 0.1 * line_sim_best],
        ],
        "\n".join(log_str),
        eval_src["meter_xxx"], eval_ref["meter_xxx"], eval_src["meter_xxx"],
        DEMO_MDESC_SRC, DEMO_MDESC_REF, DEMO_MDESC_HYP,
        DEMO_RHYME_SRC, DEMO_RHYME_REF, DEMO_RHYME_HYP,
    )
