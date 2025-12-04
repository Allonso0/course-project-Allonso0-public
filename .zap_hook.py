# ZAP hook script to customize scanning
def zap_started(zap, target):
    print(f"[ZAP Hook] Starting scan of {target}")
    pass


def zap_pre_shutdown(zap):
    print("[ZAP Hook] Scan completed")
