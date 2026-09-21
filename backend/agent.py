import psutil
import time
from datetime import datetime


# ============================================================
# SESSION DATA
# ============================================================

incident_history = []

previous_alerts = set()

metric_history = []


# ============================================================
# RECORD INCIDENTS
# ============================================================

def record_incidents(current_alerts):

    global previous_alerts

    current_alerts = set(current_alerts)

    current_time = datetime.now().strftime("%H:%M:%S")

    # New incidents
    new_alerts = current_alerts - previous_alerts

    for alert in new_alerts:

        incident_history.append({
            "time": current_time,
            "status": "WARNING",
            "message": alert
        })

    # Resolved incidents
    resolved_alerts = previous_alerts - current_alerts

    for alert in resolved_alerts:

        incident_history.append({
            "time": current_time,
            "status": "RESOLVED",
            "message": alert
        })

    previous_alerts = current_alerts

    # Keep latest 20
    if len(incident_history) > 20:

        del incident_history[:-20]


# ============================================================
# PROCESS MONITORING
# ============================================================

def get_processes():

    process_objects = []

    for process in psutil.process_iter(
        ["pid", "name", "memory_percent"]
    ):

        try:

            process.cpu_percent(None)

            process_objects.append(process)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            pass

    time.sleep(0.5)

    cpu_count = psutil.cpu_count() or 1

    processes = []

    for process in process_objects:

        try:

            info = process.info

            name = info["name"] or "Unknown"

            # Ignore Windows idle process
            if name.lower() == "system idle process":
                continue

            raw_cpu = process.cpu_percent(None)

            normalized_cpu = raw_cpu / cpu_count

            processes.append({

                "pid": info["pid"],

                "name": name,

                "cpu_percent": round(
                    normalized_cpu,
                    1
                ),

                "memory_percent": round(
                    info["memory_percent"] or 0,
                    1
                )

            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            pass

    top_cpu = sorted(
        processes,
        key=lambda x: x["cpu_percent"],
        reverse=True
    )[:5]

    top_memory = sorted(
        processes,
        key=lambda x: x["memory_percent"],
        reverse=True
    )[:5]

    return top_cpu, top_memory


# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk_score(cpu, memory, disk, alerts):

    cpu_score = min(cpu, 100)

    memory_score = min(memory, 100)

    disk_score = min(disk, 100)

    alert_score = min(len(alerts) * 25, 100)

    score = (
        cpu_score * 0.30
        + memory_score * 0.40
        + disk_score * 0.20
        + alert_score * 0.10
    )

    score = round(score)

    if score < 35:

        level = "LOW"

    elif score < 70:

        level = "MODERATE"

    elif score < 85:

        level = "HIGH"

    else:

        level = "CRITICAL"

    return score, level


# ============================================================
# TREND ANALYSIS
# ============================================================

def analyze_trends(cpu, memory, disk):

    global metric_history

    metric_history.append({

        "cpu": cpu,

        "memory": memory,

        "disk": disk

    })

    # Keep latest 10 readings
    if len(metric_history) > 10:

        metric_history.pop(0)


    trends = {

        "cpu": "STABLE",

        "memory": "STABLE",

        "disk": "STABLE"

    }


    if len(metric_history) >= 3:

        first = metric_history[0]

        last = metric_history[-1]


        # CPU trend
        if last["cpu"] - first["cpu"] >= 5:

            trends["cpu"] = "RISING"

        elif first["cpu"] - last["cpu"] >= 5:

            trends["cpu"] = "FALLING"


        # Memory trend
        if last["memory"] - first["memory"] >= 3:

            trends["memory"] = "RISING"

        elif first["memory"] - last["memory"] >= 3:

            trends["memory"] = "FALLING"


        # Disk trend
        if last["disk"] - first["disk"] >= 2:

            trends["disk"] = "RISING"

        elif first["disk"] - last["disk"] >= 2:

            trends["disk"] = "FALLING"


    predictions = []


    if trends["cpu"] == "RISING":

        predictions.append(
            "CPU usage is trending upward. "
            "Monitor high CPU processes before the system becomes overloaded."
        )


    if trends["memory"] == "RISING":

        predictions.append(
            "Memory usage is trending upward. "
            "The system may experience memory pressure if the trend continues."
        )


    if trends["disk"] == "RISING":

        predictions.append(
            "Disk usage is increasing. "
            "Consider cleaning unnecessary files before storage becomes critical."
        )


    if len(predictions) == 0:

        predictions.append(
            "No significant resource growth trend detected."
        )


    return trends, predictions


# ============================================================
# ROOT CAUSE ANALYSIS
# ============================================================

def analyze_root_cause(
    cpu,
    memory,
    disk,
    top_cpu,
    top_memory
):

    causes = []


    if cpu >= 90:

        if len(top_cpu) > 0:

            process = top_cpu[0]

            causes.append(
                "High CPU utilization is the primary issue. "
                + process["name"]
                + " is the highest CPU-consuming process."
            )

        else:

            causes.append(
                "High CPU utilization is the primary detected issue."
            )


    if memory >= 80:

        if len(top_memory) > 0:

            process = top_memory[0]

            causes.append(
                "High memory utilization detected. "
                + process["name"]
                + " is consuming the most memory among monitored processes."
            )

        else:

            causes.append(
                "High memory utilization is the primary detected issue."
            )


    if disk >= 90:

        causes.append(
            "High disk utilization detected. "
            "Storage capacity should be reviewed."
        )


    if len(causes) == 0:

        causes.append(
            "No major resource bottleneck detected. "
            "The infrastructure is operating within normal thresholds."
        )


    return causes


# ============================================================
# PROCESS HEALTH
# ============================================================

def analyze_process_health(
    top_cpu,
    top_memory
):

    combined = {}

    for process in top_cpu:

        pid = process["pid"]

        combined[pid] = process.copy()


    for process in top_memory:

        pid = process["pid"]

        if pid not in combined:

            combined[pid] = process.copy()


    health = []


    for process in combined.values():

        cpu = process["cpu_percent"]

        memory = process["memory_percent"]


        if cpu >= 50 or memory >= 15:

            status = "HIGH"

        elif cpu >= 25 or memory >= 10:

            status = "WARNING"

        else:

            status = "HEALTHY"


        health.append({

            "name": process["name"],

            "pid": process["pid"],

            "cpu_percent": process["cpu_percent"],

            "memory_percent": process["memory_percent"],

            "status": status

        })


    return health[:8]


# ============================================================
# REMEDIATION SUGGESTIONS
# ============================================================

def generate_remediation(
    cpu,
    memory,
    disk,
    top_cpu,
    top_memory
):

    actions = []


    if cpu >= 90:

        if len(top_cpu) > 0:

            process = top_cpu[0]

            actions.append(
                "Review "
                + process["name"]
                + " and close or restart it if it is not required."
            )

        else:

            actions.append(
                "Review running applications and unnecessary background processes."
            )


    elif cpu >= 75:

        actions.append(
            "Monitor CPU-consuming applications and reduce unnecessary workloads."
        )


    if memory >= 90:

        if len(top_memory) > 0:

            process = top_memory[0]

            actions.append(
                "Close unnecessary applications. "
                + process["name"]
                + " is currently the largest detected memory consumer."
            )

        else:

            actions.append(
                "Close unnecessary applications to reduce memory pressure."
            )


    elif memory >= 80:

        actions.append(
            "Close unused applications and browser tabs to reduce memory usage."
        )


    if disk >= 95:

        actions.append(
            "Free disk space immediately by removing unnecessary files."
        )

    elif disk >= 90:

        actions.append(
            "Clean temporary files and unused applications."
        )

    elif disk >= 80:

        actions.append(
            "Plan disk cleanup before storage capacity becomes critical."
        )


    if len(actions) == 0:

        actions.append(
            "No immediate remediation required. Continue monitoring the infrastructure."
        )


    return actions


# ============================================================
# MAIN SYSTEM MONITORING
# ============================================================

def get_system_metrics():

    # --------------------------------------------------------
    # SYSTEM METRICS
    # --------------------------------------------------------

    cpu = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()

    disk = psutil.disk_usage("C:\\")


    # --------------------------------------------------------
    # ALERTS
    # --------------------------------------------------------

    alerts = []


    if cpu >= 90:

        alerts.append(
            "CPU usage is very high"
        )


    if memory.percent >= 80:

        alerts.append(
            "Memory usage is high"
        )


    if disk.percent >= 90:

        alerts.append(
            "Disk usage is very high"
        )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if len(alerts) == 0:

        status = "NORMAL"

    elif (
        cpu >= 90
        or memory.percent >= 90
        or disk.percent >= 95
    ):

        status = "CRITICAL"

    else:

        status = "WARNING"


    # --------------------------------------------------------
    # PROCESSES
    # --------------------------------------------------------

    top_cpu, top_memory = get_processes()


    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    risk_score, risk_level = calculate_risk_score(
        cpu,
        memory.percent,
        disk.percent,
        alerts
    )


    # --------------------------------------------------------
    # TRENDS
    # --------------------------------------------------------

    trends, predictions = analyze_trends(
        cpu,
        memory.percent,
        disk.percent
    )


    # --------------------------------------------------------
    # ROOT CAUSE
    # --------------------------------------------------------

    root_causes = analyze_root_cause(
        cpu,
        memory.percent,
        disk.percent,
        top_cpu,
        top_memory
    )


    # --------------------------------------------------------
    # PROCESS HEALTH
    # --------------------------------------------------------

    process_health = analyze_process_health(
        top_cpu,
        top_memory
    )


    # --------------------------------------------------------
    # REMEDIATION
    # --------------------------------------------------------

    remediation = generate_remediation(
        cpu,
        memory.percent,
        disk.percent,
        top_cpu,
        top_memory
    )


    # --------------------------------------------------------
    # EXISTING RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations = []


    if cpu >= 90:

        recommendations.append(
            "CPU usage is very high. "
            "Review the top CPU-consuming processes."
        )

    elif cpu >= 75:

        recommendations.append(
            "CPU usage is getting high. "
            "Monitor the top CPU-consuming processes."
        )


    if memory.percent >= 90:

        if len(top_memory) > 0:

            recommendations.append(
                "Memory usage is critically high. "
                + top_memory[0]["name"]
                + " is the top memory-consuming process."
            )

        else:

            recommendations.append(
                "Memory usage is critically high."
            )


    elif memory.percent >= 80:

        if len(top_memory) > 0:

            recommendations.append(
                "Memory usage is high. "
                + top_memory[0]["name"]
                + " is the top memory-consuming process. "
                "Consider closing unnecessary applications."
            )

        else:

            recommendations.append(
                "Memory usage is high. "
                "Consider closing unnecessary applications."
            )


    if disk.percent >= 95:

        recommendations.append(
            "Disk space is critically low. "
            "Remove unnecessary files immediately."
        )

    elif disk.percent >= 90:

        recommendations.append(
            "Disk usage is very high. "
            "Consider cleaning temporary files."
        )

    elif disk.percent >= 80:

        recommendations.append(
            "Disk usage is getting high. "
            "Consider cleaning unnecessary files."
        )


    if len(recommendations) == 0:

        recommendations.append(
            "System resources are operating within normal limits."
        )


    # --------------------------------------------------------
    # INCIDENTS
    # --------------------------------------------------------

    record_incidents(alerts)


    # --------------------------------------------------------
    # RETURN EVERYTHING
    # --------------------------------------------------------

    return {

        "cpu_percent": cpu,

        "memory_percent": memory.percent,

        "disk_percent": disk.percent,

        "status": status,

        "alerts": alerts,

        "recommendations": recommendations,

        "top_cpu_processes": top_cpu,

        "top_memory_processes": top_memory,

        "incident_history": incident_history,

        "risk_score": risk_score,

        "risk_level": risk_level,

        "trends": trends,

        "predictions": predictions,

        "root_causes": root_causes,

        "process_health": process_health,

        "remediation": remediation

    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    metrics = get_system_metrics()

    print(metrics)