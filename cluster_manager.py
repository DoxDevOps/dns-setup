import os
import utils

cluster_endpoint = 'http://10.44.0.52/sites/api/v1/get_single_cluster/1'
site_endpoint = 'http://10.44.0.52/sites/api/v1/get_single_site/'



for site in utils.api.get_sites_from_cluster(cluster_endpoint, site_endpoint):    
    
    for fetched_site in utils.api.get_site(site, site_endpoint):

        if utils.net.ping(fetched_site['fields']['ip_address']):

            apps = ['api', 'core', 'art']   

            dir_name = {
                'api'   :   'BHT-EMR-API',
                'core'  :   'BHT-Core',
                'art'   :   'BHT-Core/apps/ART'
            }    

            app_tag = {
                'api'   :   'v4.10.25',
                'core'  :   'v4.7.8',
                'art'   :   'v4.11.3'
            }        

            for app in apps:

                if utils.files.push(app, fetched_site['fields']['username'], fetched_site['fields']['ip_address']):

                    print("Files pushed successfully.")
                    
                    # change app version/tag
                    host = fetched_site['fields']['username'] + "@" + fetched_site['fields']['ip_address']

                    directory = "/var/www/" + dir_name[app]

                    if utils.git.checkout(host, directory, app_tag[app]):

                        if app == 'api':

                            os.system("ssh " + host + " bash --login -c 'cd /var/www/BHT-EMR-API && bundle install --local && rake db:migrate && git describe > HEAD && mysql -uroot -proot openmrs < db/sql/openmrs_metadata_1_7.sql -v -f && mysql -uroot -proot openmrs < db/sql/alternative_drug_names.sql -v -f && mysql -uroot -proot openmrs < db/sql/moh_regimens_v2020.sql -v -f && mysql -uroot -proot openmrs < db/sql/bart2_views_schema_additions.sql -v -f'")

                        else:

                            os.system("ssh " + host + " bash --login -c 'cd '" + directory + "' && git describe > HEAD'")

                        print("Successfully checked out " + app + " to " + app_tag[app])

                    else:

                        print("Failed to check out " + app)
                    

                    # load meta data
                    # change status on Xi to depict successful transfer of files to site
                    # send email alert to followers or maybe generate report

                else:

                    print("Failed to transfer.")
                    # change status on Xi to depict failed transfer of files
                    # send email alert to followers or maybe generate report