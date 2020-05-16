from bs4 import BeautifulSoup
import requests
import os
import re
import sys
import shelve
import datetime

def comic_start():
    os.makedirs('existential_comics', exist_ok = True)
    exist_tracker = shelve.open('exist_tracker', writeback = True)
    base_url = 'https://existentialcomics.com'
    last_com = False

    if 'url' in exist_tracker:
        sys.stdout.write(f'Trying to pick up where we left off. \n \
            Time is now{datetime.datetime.now()}\n')
        sys.stdout.flush()
        url = exist_tracker['url']
        old_url = url
        page_num = exist_tracker['page_num']

        try:
            page = requests.get(url)
            page_soup = BeautifulSoup(page.content, 'html5lib')

        except Exception as err:
            sys.stdout.write(f'Error connecting to the Server\n \
                Error is {err}\
                Operation aborted. Time is now: {datetime.datetime.now()}\n')
            sys.stdout.flush()
            return 'Error!'

        last_test = page_soup.find_all('img',{'src':re.compile('nav_end_b.jpg')})
        if len(last_test) > 0:
            sys.stdout.write(f'No new comics since last run.\n Ending operation.\n Time is now: {datetime.datetime.now()}')
            last_com = True

        else:
            sys.stdout.write('Finding next comic...\n')
            sys.stdout.flush()
            next_img = page_soup.find_all('img',{'src':re.compile('nav_next.jpg')})
            next_url = next_img[0].parent['href']
            url = f'{base_url}{next_url}'

    else:
        page_num = 1
        url = 'http://existentialcomics.com/comic/1'
        old_url = url
        sys.stdout.write(f'Initial project beginning!\n Time is now: {datetime.datetime.now()}\n')
        sys.stdout.flush()

    while last_com == False:
        try:
            exist_comic = requests.get(url)
            exist_soup = BeautifulSoup(exist_comic.content, 'html5lib')
            com_imgs = exist_soup.find_all(class_ = 'comicImg')
            
            if len(com_imgs) > 1:
                track_num = 1
                for com in com_imgs:
                    com_url = com.get('src')
                    check = downloader(f'http:{com_url}', f'{page_num}_{track_num}')
                    if check == False:
                        raise NameError('Download Error!')
                    else:
                        track_num += 1

            else:
                com_url = com_imgs[0].get('src')
                check = downloader(f'http:{com_url}', f'{page_num}')
                if check == False:
                    raise NameError('Download Error!')

        except Exception as err:
            sys.stdout.write(f'Error downloading comic {page_num} at {url}.\n \
                Exception was: {err} \n \
                Halting operations and saving location.\n Time is now {datetime.datetime.now()}\n')
            sys.stdout.flush()
            exist_tracker['page_num'] = page_num
            exist_tracker['url'] = old_url
            exist_tracker.close()
            return 'Error!'

        try:
            last_test = exist_soup.find_all('img',{'src':re.compile('nav_end_b.jpg')})
            if len(last_test) > 0:
                exist_tracker['url'] = url
                exist_tracker['page_num'] = page_num
                exist_tracker.close()
                sys.stdout.write(f"We've come to the end of the comic for now. Saving progress. {datetime.datetime.now()}\n")
                sys.stdout.flush()
                last_com = True

            else:
                next_img = exist_soup.find_all('img',{'src':re.compile('nav_next.jpg')})
                next_url = next_img[0].parent['href']
                old_url = url
                url = f'{base_url}{next_url}'
                page_num += 1

        except Exception as err:
            # I originally thought of breaking the error cycle into a couple parts. Then I realized it added nothing. Whoops.
            sys.stdout.write(f'This state should never be triggered. Really, if you have, good job! Time is {datetime.datetime.now()} \n \
                The error: {err}. Congrats on triggering it. \n \
                Saving progress and ending.')
            exist_tracker['url'] = url
            page_num += 1
            exist_tracker['page_num'] = page_num
            exist_tracker.close()
            return 'Error!'

    

def downloader(comurl, name):
    try:
        comdown = requests.get(comurl)
        comend = comurl[-4:]
        comname = f'exist_{name}{comend}'
        sys.stdout.write(f'Downloading comic number: {name}\n')
        sys.stdout.flush()
        imageFile = open(os.path.join('existential_comics', os.path.basename(comname)), 'wb')
        for chunk in comdown.iter_content(100_000):
                        imageFile.write(chunk)
        imageFile.close()
        return True
    except:
        return False



def main():
    comic_start()

if __name__ == '__main__':
    main()