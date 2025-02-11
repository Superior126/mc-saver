import yaml
import os
import json

class ConfigInterface:
    def __init__(self):
        self.config = None

        # Check if config dir exists
        if not os.path.exists('/etc/mc_saver'):
            os.makedirs('/etc/mc_saver')

        # Get current run directory
        self.run_dir = os.path.dirname(os.path.realpath(__file__))

        # Load config template
        with open(self.run_dir + '/../resources/config_template.json', 'r') as f:
            self.config_template = json.loads(f.read())
            f.close()

        # Check if config file exists
        if not os.path.exists('/etc/mc_saver/config.yaml'):
            with open('/etc/mc_saver/config.yaml', 'w') as f:
                f.write(yaml.dump(self.config_template))
                f.close()
        else:
            # Load config file
            with open('/etc/mc_saver/config.yaml', 'r') as f:
                self.config = yaml.load(f, Loader=yaml.FullLoader)
                f.close()
            
            # Ensure all keys are present
            for key in self.config_template.keys():
                if key not in self.config:
                    self.config[key] = self.config_template[key]

            # Save config file
            with open('/etc/mc_saver/config.yaml', 'w') as f:
                f.write(yaml.dump(self.config))
                f.close()
