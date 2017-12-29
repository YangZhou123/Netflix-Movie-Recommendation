import json
import requests

# C:\Users\Fred\AppData\Roaming\Python\Scripts\scrapy.exe runspider OMDB_spider.py

def get_details(id, year, name):
    try:
        url = 'http://www.omdbapi.com/?t=' + name + '&y=' + str(year) + '&plot=full&r=json'
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
    movie_titles_f = open('../data_set/nf_prize_dataset/movie_titles.txt')

    # details = get_details(1, "1998", "Shakespeare in Love")
    # print details

    for movie_title in movie_titles_f.readlines():
        collection = movie_title.split(',')

        if len(collection) > 0:
            id = collection[0]
            year = collection[1]
            name = collection[2]

            if int(id) > 6483:
                details = get_details(id, year, name)
                print details

                with open('../data_set/movie_details_api_1-2.txt', 'a') as outfile:
                    json.dump(details, outfile)
                    outfile.write('\n')

    movie_titles_f.close()


if __name__ == "__main__":
    main()