import json
import requests
import os

# C:\Users\Fred\AppData\Roaming\Python\Scripts\scrapy.exe runspider OMDB_spider.py

def get_details_on_title(id, year, name):
    try:
        url = 'http://www.omdbapi.com/?t=' + name + '&y=&plot=full&r=json'
        response = requests.get(url).json()

        if response["Response"] == u'False':
            dict = {'id': id, 'Year': year, 'Title': name}
            return dict
        else:
            response["id"] = id
            return response
    except:
        dict = {'id': id, 'Year': year, 'Title': name}
        return dict


def main():
    path = '../data_set/movie_details_api_1'

    for f in os.listdir(path):
        movie_details_f = open(os.path.join(path, f))

        count = 0
        for movie_details in movie_details_f.readlines():
            json_details = json.loads(movie_details)

            # check if Plot exists
            if 'Plot' in json_details:
                # save to the file directly
                with open('../data_set/movie_details_api_2/details.txt', 'a') as outfile:
                    json.dump(json_details, outfile)
                    outfile.write('\n')
            else:
                # run the api based on the title only
                count += 1

                details = get_details_on_title(json_details['id'], json_details['Year'], json_details['Title'])
                print details

                with open('../data_set/movie_details_api_2/details.txt', 'a') as outfile:
                    json.dump(json_details, outfile)
                    outfile.write('\n')

            movie_details_f.close()

        print "num of movies does not have details: "
        print count


if __name__ == "__main__":
    main()