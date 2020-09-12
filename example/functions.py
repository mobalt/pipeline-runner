import os


def example_function(REQUIRED, WITH_DEFAULT_VALUE="default"):
    return {"SET_THIS_VARIABLE": "1", "DEFAULTED": WITH_DEFAULT_VALUE}


def check_required_variables():
    pass


def split_subject(SUBJECT):
    components = SUBJECT.split(":")
    if len(components) != 4:
        raise ValueError(
            "Expecting a colon-delimited SUBJECT in the format AA:BB:CC:DD, instead got: ",
            SUBJECT,
        )

    proj, subject_id, classifier, extra = components
    return {
        "PROJECT": proj,
        "SUBJECT_ID": subject_id,
        "SUBJECT_CLASSIFIER": classifier,
        "SUBJECT_EXTRA": extra,
        "SESSION": f"{subject_id}_{classifier}",
    }


def choose_node():
    pass


def chain_jobs_on_pbs():
    pass


def make_directories(WORKING_DIR):
    os.makedirs(WORKING_DIR, exist_ok=True)
