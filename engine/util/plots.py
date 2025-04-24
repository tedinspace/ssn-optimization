import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from engine.environment.sensors.GroundSensor import SensorGeneralStatus

def c_map(keys):
    '''get color maps for keys'''
    return {key: f"C{idx % 10}" for idx, key in enumerate(keys)}

def basic_uncertainty_plot(loaded_tracker):
    color_map = c_map(loaded_tracker.sat_keys)

    plt.figure(figsize=(10, 6))
    for object_id, obj_data in loaded_tracker.uncertainty_trajs.items():
        plt.plot(obj_data['times'], obj_data['sigma_X'], label=object_id, color=color_map[object_id])

    plt.xlabel('Time [mjd]')
    plt.ylabel('Uncertainty [meters]')
    plt.title('Uncertainty vs Time for')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.yscale('log')
    plt.show()

def basic_ground_sensor_plot_v1(loaded_tracker):
    '''
        includes
            1. tracking times by sensor
            2. maneuver times (colored by object)
            3. online/offline times
    '''
    sensor_names = list(loaded_tracker.sensor_keys)

    color_map = c_map(loaded_tracker.sat_keys)

    fig, ax = plt.subplots(figsize=(12, 6))
    
    
    if loaded_tracker.tasking_record:
        for sensor_idx, sensor_key in enumerate(sensor_names):
            for sat_key in loaded_tracker.tasking_record[sensor_key]:
                color = color_map[sat_key]
                for message in loaded_tracker.tasking_record[sensor_key][sat_key]:
                    start = message.record.scheduled_start.mjd
                    end = message.record.scheduled_end.mjd
                    ax.broken_barh(
                        [(start, end - start)],
                        (sensor_idx - 0.4, 0.8),
                        facecolors=color
                    )
    else:
        start = loaded_tracker.scenario_configs.scenario_epoch.mjd
        end = loaded_tracker.scenario_configs.scenario_end.mjd
        for sensor_idx, sensor_key in  enumerate(sensor_names):
            ax.broken_barh(
                            [(start, end - start)],
                            (sensor_idx - 0.4, 0.8),
                            facecolors="white"
                        )
    


    

    ax.set_yticks(range(len(sensor_names)))
    ax.set_yticklabels(sensor_names)

    ax.set_xlabel("MJD Time")
    ax.set_ylabel("Sensors")
    ax.set_title("Sensor Tasking Schedule")

    # maneuvers
    for sat_k in loaded_tracker.maneuver_truth_record:
        maneuvers = loaded_tracker.maneuver_truth_record[sat_k]
        for m in maneuvers:
            ax.axvline(x=m.time.mjd, color=color_map[sat_k], linestyle='--', linewidth=1)

    for sensor_k in loaded_tracker.sensor_availability:
        type_and_times = loaded_tracker.sensor_availability[sensor_k]
        for i in range(len(type_and_times[0])):
            color = 'green'
            if type_and_times[0][i]==SensorGeneralStatus.OFFLINE:
                color = 'red'
            ax.axvline(x=type_and_times[1][i].mjd, color=color, linestyle='-', linewidth=1)
            ax.text(
            type_and_times[1][i].mjd, ax.get_ylim()[1], 
            sensor_k,
            verticalalignment='bottom',
            horizontalalignment='right',
            fontsize=9,
            color=color,
        )
        
    # Legend
    legend_patches = [mpatches.Patch(color=color_map[k], label=str(k)) for k in color_map]
    ax.legend(handles=legend_patches, title="Satellite Key", bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()
    return fig, ax