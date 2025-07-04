import logging, uuid, os
from flask import request, g

def init_logging(app):
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(filename="logs/access.log", level=logging.INFO, format="%(message)s")

    @app.before_request
    def start_log():
        g.log_id = str(uuid.uuid4())
        log = {
            "logID": g.log_id,
            "method": request.method,
            "path": request.path,
            "ip": request.remote_addr,
            "message": "log recorded"
        }
        logging.info(log)

    @app.after_request
    def attach_log_id(res):
        res.headers["X-Log-ID"] = getattr(g, "log_id", "none")
        return res
