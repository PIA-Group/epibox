def close_file(a_file, annot_file, log_drift_file):
    close_acq_file(a_file)
    close_drift_log_file(log_drift_file)

def close_acq_file(a_file):
	a_file.close()


def close_drift_log_file(drift_log_file):
	drift_log_file.close()

