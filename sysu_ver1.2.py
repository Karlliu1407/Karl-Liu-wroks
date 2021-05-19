import requests
from bs4 import BeautifulSoup
import time
import json
import csv
import codecs
import sys
import os
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

delay = 2 #浏览器单位延时片

def getsoup(url):
    headers = {
        'Connection' : 'close'
        ,'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    '''
    --Bug: 网页出现反爬虫报错: "Max retries exceeded with url"
    --Cause: Sending too many requests from same ip address in short period of time
             原因是系统打开代理, 但还没有打开ssr连接
    --Solution: VPS可解决
    '''
    
    res = requests.get(url)
    res.encoding = 'utf-8'
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def is_site(string):
    stringset2 = []
    stringset2.append('师资队伍')
    stringset2.append('师资团队')
    stringset2.append('师资力量')
    stringset2.append('岭院师资')
    stringset2.append('师资')
    stringset2.append('学科人才')
    stringset2.append('人员')
    stringset2.append('教师')
    stringset2.append('教师名录')
    stringset2.append('教师名单')
    stringset2.append('教授')
    stringset2.append('教师系列')
    stringset2.append('客座、讲座、兼职教授')
    stringset2.append('英语系')
    stringset2.append('人才队伍')
    stringset2.append('中心介绍')
    stringset2.append('导师风采')
    if string in stringset2:
        return True
    return False

def is_site_2(string): ## 排除所有难以处理的学院网站
    stringset = []
    stringset.append('实验动物中心')
    stringset.append('心理健康教育咨询中心')
    stringset.append('光华口腔医学院')
    if string in stringset:
        return True
    return False

def visit(url): #抓各个学院'师资','人才'网页分页
        
    soup = getsoup(url)
    pages = []
    for site in soup.find_all('a'):
        if is_site(site.text): #判定是否是'师资'页面
            link = url + '/' + site.get('href').lstrip('/') #接上父节点
            if link not in pages: #去重
                pages.append(link)

    return pages

def safari(url): #在师资页面收集教师名录, 并记录职位
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.set_window_position(0, 0)
    # driver.maximize_window()
    driver.set_window_size(1550, 600)
    driver.get(url)
    time.sleep(2*delay)
    teachers = []
    # ========= >按学院分情况抓取< =========
    if "chinese" in url:
        for item in driver.find_elements_by_css_selector("[class='item-list']"):
            title = item.find_element_by_tag_name("h3").text
            for name in item.find_elements_by_tag_name("a"):
                teachers.append({"Title": title, "Name": name.text})

    if "history" in url: #历史学院
        subjects = driver.find_elements_by_class_name("nchannel")
        links = [subject.find_element_by_tag_name("a").get_attribute("href") for subject in subjects]
        while True:
            #按学科建link池, 使用队列遍历
            titles = driver.find_elements_by_tag_name("p")
            members = driver.find_elements_by_class_name("member")
            for p, title in enumerate(titles):
                endline = titles[p + 1].location['y'] if (p + 1< len(titles)) else 99999
                #用前后两个标签位置来锁定教师对应的职称, endline为职该位老师的下分界线
                for member in members:
                    if title.location['y'] < member.location['y'] < endline:
                        teachers.append({"Title": title.text, "Name": member.text.split()[0]})
            if not links:
                break
            driver.get(links[0])
            driver.refresh()
            time.sleep(delay)
            links.pop(0)

    if 'lac'in url: #博雅学院 :
        teachers.append({'Title':'教授',"Name":'张卫红'})
        teachers.append({'Title':'副教授',"Name":'王承教'})
        teachers.append({'Title':'副教授',"Name":'董波'})
        teachers.append({'Title':'教授',"Name":'刘志荣'})
        teachers.append({'Title':'讲师',"Name":'陈探宇'})
        teachers.append({'Title':'讲师',"Name":'黄俊松'})
        teachers.append({'Title':'讲师',"Name":'杨砚'})
        teachers.append({'Title':'讲师',"Name":'刘海川'})
        teachers.append({'Title':'副教授',"Name":'吴海'})
        teachers.append({'Title':'讲师',"Name":'陈慧'})
        teachers.append({'Title':'副教授',"Name":'程方毅'})
        teachers.append({'Title':'讲师',"Name":'胡劲茵'})
        teachers.append({'Title':'副教授',"Name":'肖文明'})
        teachers.append({'Title':'讲师',"Name":'朱坤荣'})
    
    if "philosophy" in url:
        lists = driver.find_element_by_class_name("schannel").find_elements_by_tag_name("li")
        links = [ls.find_element_by_tag_name("a").get_attribute("href") for ls in lists]
        for link in links:
            if "04" in link: #特判"专职教师（按职称）"页面
                continue
            driver.get(link)
            driver.refresh()
            time.sleep(delay)
            table = driver.find_element_by_class_name("maintable")
            for tr in table.find_elements_by_tag_name("tr"):
                tds = tr.find_elements_by_xpath("./td[@align='center']")
                #这里要用./表示在本行内的td, 若是用//则是页面内全部td都能被检索
                if len(tds) >= 2:
                    teachers.append({"Title": tds[1].text, "Name": tds[0].text})


    if 'ssa' in url: #社会人文学院
        lsts = driver.find_elements_by_class_name('views-teacher')
        links_ssa=[]
        for i in lsts:
            teachers_ssa=i.find_elements_by_tag_name('a')
            for j in teachers_ssa:
                teacher_ssa=j.get_attribute('href')
                links_ssa.append(teacher_ssa)
        for k in links_ssa:
            try:
                driver.get(k)      
                title=driver.find_element_by_css_selector("[class='views-field views-field-category']").find_element_by_tag_name('a')
                name=driver.find_element_by_class_name('align-center').find_element_by_tag_name('strong')
                teachers.append({'Title':title.text,"Name":name.text})
            except:
                pass

    if 'lingnan' in url:#岭南学院
        links_ln=[]
        driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul/li[1]/ul/li[2]/a').click()
        lst_ln=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul/li[1]/ul/li[2]/ul').find_elements_by_tag_name('li')
        for i in lst_ln:
            links_ln.append(i.find_element_by_tag_name('a').get_attribute('href'))
        for j in links_ln:
            driver.get(j)
            titles_ln=driver.find_elements_by_class_name('item-list')
            for k in titles_ln:
                title_ln=k.find_element_by_tag_name('h3').text
                names_ln=k.find_elements_by_tag_name('a')
                for s in names_ln:
                    name_ln=s.text
                    teachers.append({'Title':title_ln,"Name":name_ln})

    if 'sog' in url: #政治学院
        links_sog=[]
        lst_sog=driver.find_element_by_xpath('//*[@id="block-menu-block-2"]/div/ul').find_elements_by_tag_name('li')
        for i in lst_sog:
            links_sog.append(i.find_element_by_tag_name('a').get_attribute('href'))
        for j in links_sog:
            try:
                driver.get(j)
                title_sog=driver.find_element_by_class_name('page-header').text
                names_sog=driver.find_element_by_class_name('touxiang').find_elements_by_tag_name('span')
                for k in names_sog:
                    teachers.append({'Title':title_sog,"Name":k.text})
            except:
                pass 

    if 'law' in url: #法学院
        try:
            links_law=[]
            members_law=driver.find_elements_by_css_selector("[class='members']")
            for i in members_law:
                member_law=i.find_elements_by_css_selector("[class='list-images-3-1 outside-min-tb']")
                for j in member_law:
                    member_link_law=j.find_element_by_tag_name('a')
                    member_link_law_for_lst = member_link_law.get_attribute('href')
                    links_law.append(member_link_law_for_lst)
            for k in links_law:
                driver.get(k)
                title=driver.find_element_by_css_selector("[class='views-field views-field-category']").find_element_by_class_name('field-content')
                name=driver.find_element_by_class_name('align-center').find_element_by_tag_name('strong')
                teachers.append({'Title':title.text,"Name":name.text})
        except:
            pass

    if 'ischool' in url: #资讯管理学院
        data_is=driver.find_element_by_css_selector('[class="views-table cols-0 table table-condensed table-0 table-0 table-0"]').find_elements_by_css_selector('[class="views-field views-field-field-xingming views-align-left"]')
        for i in data_is:
            name_is=i.find_element_by_tag_name('h3').text
            title_is=i.find_element_by_tag_name('a').text
            teachers.append({'Title':title_is,"Name":name_is})
    
    if 'bus' in url: #管理学院
        members_bus=driver.find_elements_by_class_name('views_faculty_right_wrap')
        for i in members_bus: 
            try:
                name=i.find_element_by_class_name('views_faculty_title').find_element_by_xpath("./a")
                title=i.find_element_by_class_name('views_faculty_position').find_element_by_xpath("./b")
                teachers.append({'Title':title.text,"Name":name.text})
            except:
                pass

    if 'mkszy' in url:#马克思主义
        links_mkszyxy=[]
        titles_mkszyxy=driver.find_element_by_xpath('//html/body/div[4]/div[1]/div[2]/ul/li[2]/ul').find_elements_by_tag_name('li')
        for i in titles_mkszyxy:
            link_mkszyxy=i.find_element_by_tag_name('a').get_attribute('href')
            links_mkszyxy.append(link_mkszyxy)
        for j in links_mkszyxy:
            driver.set_window_position(0, 0)
            driver.set_window_size(1550, 600)
            driver.get(j)
            lst_mkszyxy=driver.find_element_by_class_name('news-list').find_elements_by_class_name('news-title')
            title_mkszyxy=driver.find_element_by_class_name('sub-title').text
            for k in lst_mkszyxy:
                
                if 'A' < k.find_element_by_tag_name('a').text.split()[0][0] < 'z':
                    name_mkszyxy=k.find_element_by_tag_name('a').text
                else:
                    name_mkszyxy=k.find_element_by_tag_name('a').text.split()[0]
                teachers.append({'Title':title_mkszyxy,"Name":name_mkszyxy})
    
    if 'psy' in url:#心理学院
        try:
            links_psy=[]
            titles_psy=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('li')
            for i in titles_psy:
                link_psy=i.find_element_by_tag_name('a').get_attribute('href')
                links_psy.append(link_psy)
            for j in links_psy:
                driver.set_window_position(0, 0)
                driver.set_window_size(1550, 600)
                driver.get(j)
                lst_psy=driver.find_elements_by_css_selector("[class='list-title one-line']")
                for k in lst_psy:
                    name_psy=k.find_element_by_tag_name('strong').text
                    title_psy=k.find_element_by_tag_name('span').text
                    teachers.append({'Title':title_psy,"Name":name_psy})
        except:
            pass
        
    
    if 'scd' in url: # 传媒学院
        try:
            links_scd=[]
            titles_scd=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('li')
            for i in titles_scd:
                link_scd=i.find_element_by_tag_name('a').get_attribute('href')
                links_scd.append(link_scd)
            for j in links_scd:
                driver.set_window_position(0, 0)
                driver.set_window_size(1550, 600)
                driver.get(j)
                lst_scd=driver.find_elements_by_css_selector("[class='list-title one-line']")
                for k in lst_scd:
                    name_scd=k.find_element_by_tag_name('strong').text
                    title_scd=k.find_element_by_tag_name('span').text
                    teachers.append({'Title':title_scd,"Name":name_scd})
        except:
            pass

    if 'art' in url: #艺术
        try:
            titles_art=driver.find_elements_by_class_name("list-title")
            for i in titles_art:
                name_art=i.find_element_by_class_name('teacher-title').text
                title_art=i.find_element_by_class_name('category-title').text
                teachers.append({'Title':title_art,"Name":name_art})
        except:
            pass


    if 'math' in url: #数学
        links_math=[]
        titles_math=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('li')
        for i in titles_math:
            link_math=i.find_element_by_tag_name('a').get_attribute('href')
            links_math.append(link_math)
        for j in links_math:
            driver.set_window_position(0, 0)
            driver.set_window_size(1550, 600)
            driver.get(j)
            try:
                lst_math=driver.find_elements_by_css_selector("[class='list-title one-line']")
                for k in lst_math:
                    name_math=k.find_element_by_tag_name('strong').text
                    title_math=k.find_element_by_tag_name('span').text
                    teachers.append({'Title':title_math,"Name":name_math})
            except:
                pass

    if 'spe' in url:#物理学院
        titles_phys=driver.find_element_by_xpath('//*[@id="block-system-main"]/div/div/div').find_elements_by_class_name('item-list')
        for i in titles_phys:
            title_phys=i.find_element_by_tag_name('h3').text
            names_phys=i.find_elements_by_tag_name('li')
            for j in names_phys:
                name_phys=j.find_element_by_tag_name('a').text
                teachers.append({'Title':title_phys,"Name":name_phys})
    

    if 'ce' in url: #化学院
        lsts_ce = driver.find_elements_by_class_name('views-teacher')
        links_ce=[]
        for i in lsts_ce:
            teachers_ce=i.find_elements_by_tag_name('a')
            for j in teachers_ce:
                teacher_ce=j.get_attribute('href')
                links_ce.append(teacher_ce)
        for k in links_ce:
            try:
                driver.get(k)      
                title_ce=driver.find_element_by_css_selector("[class='views-field views-field-category']").find_element_by_class_name('field-content')
                name_ce=driver.find_element_by_class_name('align-center').find_element_by_tag_name('strong')
                teachers.append({'Title':title_ce.text,"Name":name_ce.text})
            except:
                pass


    if 'lifescience' in url: #生命科学院
        lst_lfs=driver.find_elements_by_id('block-profits-professor-block')
        for i in lst_lfs:
            title_lfs=i.find_element_by_tag_name('h2').text
            profs_lfs=i.find_elements_by_class_name('teacher-list-item')
            for j in profs_lfs:
                name_lfs=j.find_element_by_tag_name('span').text
                teachers.append({'Title':title_lfs,"Name":name_lfs})
        
        lst_lfs=driver.find_elements_by_id('block-profits-viceprofessor-block')
        for i in lst_lfs:
            title_lfs=i.find_element_by_tag_name('h2').text
            profs_lfs=i.find_elements_by_class_name('teacher-list-item')
            for j in profs_lfs:
                name_lfs=j.find_element_by_tag_name('span').text
                teachers.append({'Title':title_lfs,"Name":name_lfs})
        
        lst_lfs=driver.find_elements_by_id('block-profits-viceprofessor-block')
        for i in lst_lfs:
            title_lfs=i.find_element_by_tag_name('h2').text
            profs_lfs=i.find_elements_by_class_name('teacher-list-item')
            for j in profs_lfs:
                name_lfs=j.find_element_by_tag_name('span').text
                teachers.append({'Title':title_lfs,"Name":name_lfs})

        lst_lfs=driver.find_elements_by_id('block-profits-lecturer-block')
        for i in lst_lfs:
            title_lfs=i.find_element_by_tag_name('h2').text
            profs_lfs=i.find_elements_by_class_name('teacher-list-item')
            for j in profs_lfs:
                name_lfs=j.find_element_by_tag_name('span').text
                teachers.append({'Title':title_lfs,"Name":name_lfs})
        
        lst_lfs=driver.find_elements_by_id('block-profits-fulltimeresearcher-block')
        for i in lst_lfs:
            title_lfs=i.find_element_by_tag_name('h2').text
            profs_lfs=i.find_elements_by_class_name('teacher-list-item')
            for j in profs_lfs:
                name_lfs=j.find_element_by_tag_name('span').text
                teachers.append({'Title':title_lfs,"Name":name_lfs})


    if 'gp' in url: #地理学院
        links_gp_1=[]
        links_gp_2=[]
        lst_gp=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('li')
        for i in lst_gp:
            links_gp_1.append(i.find_element_by_tag_name('a').get_attribute('href'))
        for j in links_gp_1:
            driver.get(j)
            titles_gp=driver.find_element_by_class_name('quicktabs-wrapper').find_element_by_tag_name('ul').find_elements_by_tag_name('li')
            for k in titles_gp:
                k.find_element_by_tag_name('a').click()
                profs_gp=driver.find_elements_by_css_selector('[class="list-title one-line"]')
                for o in profs_gp:
                    title_gp=o.find_element_by_tag_name('span').text
                    name_gp=o.find_element_by_tag_name('strong').text
                    if title_gp and name_gp != None:
                        teachers.append({'Title':title_gp,"Name":name_gp})

    if 'mse' in url: #材料科学
        titles_mse=driver.find_elements_by_class_name('faculty')
        for i in titles_mse:
            title_mse=i.find_element_by_tag_name('h3').text
            names_mse=i.find_elements_by_tag_name('a')
            for j in names_mse:
                teachers.append({'Title':title_mse,"Name":j.text})
        but_mse=driver.find_element_by_class_name('next').find_element_by_tag_name('a').click()
        titles_mse=driver.find_elements_by_class_name('faculty')
        for i in titles_mse:
            title_mse=i.find_element_by_tag_name('h3').text
            names_mse=i.find_elements_by_tag_name('a')
            for j in names_mse:
                teachers.append({'Title':title_mse,"Name":j.text})

    if 'seit' in url:#电子工程
        titles_seit=driver.find_elements_by_class_name('seitfaculty')
        for i in titles_seit:
            title_seit=i.find_element_by_tag_name('h3').text
            names_seit=i.find_elements_by_tag_name('a')
            for j in names_seit:
                teachers.append({'Title':title_seit,"Name":j.text})

    if 'sdcs' in url: #信息工程
        titles_sdcs=driver.find_elements_by_class_name('xisuo')
        for i in titles_sdcs:
            title_sdcs=i.find_element_by_tag_name('h3').text
            names_sdcs=i.find_elements_by_tag_name('strong')
            for j in names_sdcs:
                teachers.append({'Title':title_sdcs,"Name":j.text})

    if 'sese' in url:#材料学院
        links_se=[]
        driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul/li[2]/a').click()
        lst_se=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('a')
        for i in lst_se:
            links_se.append(i.get_attribute('href'))
        for j in links_se:
            driver.get(j)
            titles_se=driver.find_element_by_css_selector("[class='views-element-container block']").find_elements_by_class_name('item-list')
            for k in titles_se:
                title_se=k.find_element_by_tag_name('h3').text
                names_se=k.find_elements_by_tag_name('a')
                for o in names_se:
                    name_se=o.text
                    teachers.append({'Title':title_se,"Name":name_se})

    if 'ssse' in url: #系统科学
        teachers.append({'Title':'教授',"Name":'陈洪波'})
        teachers.append({'Title':'副教授',"Name":'段焰辉 '})
        teachers.append({'Title':'副教授',"Name":'孙 蕾'})
        teachers.append({'Title':'教授',"Name":'张英朝'})
        teachers.append({'Title':'助理教授',"Name":'王劲博'})
        teachers.append({'Title':'助理教授',"Name":'张岐良'})
        teachers.append({'Title':'助理教授',"Name":'侯治威'})
        teachers.append({'Title':'博士后',"Name":'钟福利'})
        teachers.append({'Title':'专职研究人员',"Name":'修保新'})
        teachers.append({'Title':'专职研究人员',"Name":'纪思婷'})

    if 'sph' in url: #公共卫生学院
        try:
            links_sph=[]
            titles_sph=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('li')
            for i in titles_sph:
                link_sph=i.find_element_by_tag_name('a').get_attribute('href')
                links_sph.append(link_sph)
            for j in links_sph:
                driver.get(j)
                lst_sph=driver.find_elements_by_css_selector("[class='list-title one-line']")
                for k in lst_sph:
                    name_sph=k.find_element_by_tag_name('strong').text
                    title_sph=k.find_element_by_tag_name('span').text
                    teachers.append({'Title':title_sph,"Name":name_sph})
        except:
            pass

    if 'nursing' in url:#护理学院
        try:
            links_nurs=[]
            titles_nurs=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('li')
            for i in titles_nurs:
                link_nurs=i.find_element_by_tag_name('a').get_attribute('href')
                links_nurs.append(link_nurs)
            for j in links_nurs:
                driver.get(j)
                lst_nurs=driver.find_elements_by_css_selector("[class='list-title one-line']")
                for k in lst_nurs:
                    name_nurs=k.find_element_by_tag_name('strong').text
                    title_nurs=k.find_element_by_tag_name('span').text
                    teachers.append({'Title':title_nurs,"Name":name_nurs})
        except:
            pass
    
    if 'fls' in url: #外国语
        dp_fls=driver.find_element_by_xpath('//*[@id="block-menu-block-4"]/div/ul').find_elements_by_tag_name('li')
        links_fls=[]
        for i in dp_fls:
            links_fls.append(i.find_element_by_tag_name('a').get_attribute('href'))
        for j in links_fls:
            driver.get(j)
            try:
                pp_fls=driver.find_element_by_class_name('touxiang').find_elements_by_tag_name('li')
                for k in pp_fls:
                    info_fls=k.text.split()
                    s=' '.join(info_fls[:-1])
                    teachers.append({'Title':info_fls[-1],"Name":s})
            except:
                pass

    if 'zssom' in url:#医学院
        links_zs=[]
        driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul/li[2]/a').click()
        lst_zs=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('a')
        for i in lst_zs:
            try:
                links_zs.append(i.get_attribute('href'))
            except:
                pass
        for j in links_zs:
            try:
                driver.get(j)
                titles_za=driver.find_element_by_css_selector("[class='views-element-container block']").find_elements_by_class_name('item-list')
                for k in titles_za:
                    title_zs=k.find_element_by_tag_name('h3').text
                    names_zs=k.find_elements_by_tag_name('a')
                    for o in names_zs:
                        name_zs=o.text
                        teachers.append({'Title':title_zs,"Name":name_zs})
            except:
                pass

    if 'sps' in url: #药学院
        links_sps=[]
        lst_sps=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('a')
        for i in lst_sps:
            try:
                links_sps.append(i.get_attribute('href'))
            except:
                pass
        for j in links_sps:
            try:
                driver.get(j)
                titles_sps=driver.find_element_by_css_selector("[class='views-element-container block']").find_elements_by_class_name('item-list')
                for k in titles_sps:
                    title_sps=k.find_element_by_tag_name('h3').text
                    names_sps=k.find_elements_by_tag_name('a')
                    for o in names_sps:
                        name_sps=o.text
                        teachers.append({'Title':title_sps,"Name":name_sps})
            except:
                pass

    if 'yss' in url:#逸仙学院
        links_yss=[]
        lst_yss=driver.find_element_by_xpath('//*[@id="content"]/article/div/div/div[2]/div[1]/div/div/div/div/ul').find_elements_by_tag_name('a')
        for i in lst_yss:
            try:
                links_yss.append(i.get_attribute('href'))
            except:
                pass
        for j in links_yss:
            try:
                driver.get(j)
                titles_yss=driver.find_element_by_css_selector("[class='views-element-container block']").find_elements_by_class_name('item-list')
                for k in titles_yss:
                    title_yss=k.find_element_by_tag_name('h3').text
                    names_yss=k.find_elements_by_tag_name('a')
                    for o in names_yss:
                        name_yss=o.text
                        teachers.append({'Title':title_yss,"Name":name_yss})
            except:
                pass
    
    if 'tiyu' in url:#体育部
        jiaoshou=['张保华','范振国','李静波','张新萍','范宏伟']
        fujioahsou=['陈卓源','宋一心','黄志荣','李蓬','吴元生','李秀华','何江海','龙国强'
        ,'杨茜','杨波','屈萍','梁恒','武东海','蔡永茂','李铁鸣','康寅','商瑞花','张洁雯','彭伟群'
        ,'肖红','仇亚宾','李毅','刘一阳','刘靖东','邹玉铎','杨利春','罗曦娟','罗微']
        gaojijiangshi=['郑建民','林静波','曾李萍','李小兵']
        zhuanrenjiaoyuan=['谈丰田','邱天贵','陈理标','曾宪波','陈亚金','刘思华','李俊'
        ,'宋花香','凌丽平','张晓宇','王锋']
        jiangshi=['赵云雷','明应安','李寅','王守力','陈祥慧','李朝阳','张淼','王国咏','王磊'
        ,'欧阳建飞','周才']
        for i in jiaoshou:
            teachers.append({'Title':'教授',"Name":i})
        for j in fujioahsou:
            teachers.append({'Title':'副教授',"Name":j})
        for k in gaojijiangshi:
            teachers.append({'Title':'高级教师',"Name":k})
        for o in zhuanrenjiaoyuan:
            teachers.append({'Title':'专任教员',"Name":o})
        for s in jiangshi:
            teachers.append({'Title':'讲师',"Name":s})

    driver.quit()
    return teachers

def parse(soup):

    campus = soup.find_all('h1')[0].text #限定在广州校区
    schools = soup.find_all('div', id='cont')[0].find_all('a')
    datagram = []
    for inde,school in enumerate(schools):
        if not is_site_2(school.text):
        # 按学院建表)
            dataframe = {}
            dataframe['School'] = school.text.strip()
            dataframe['Homepage'] = school.get('href').rstrip('/') #各个学院网址
            dataframe['Sidepages'] = visit(dataframe['Homepage'])
            teachers = []
            sidepage = dataframe['Sidepages'][0]
            print("\n>>Safari at:", dataframe['School'])
            for teacher in safari(sidepage):
                if teacher not in teachers: #去重
                    teachers.append(teacher)
            print("\n>>Get total: ", len(teachers))
            dataframe['Teachers'] = teachers
            print(dataframe)
            datagram.append(dataframe)
    with open('tmp.json', 'w', encoding='utf-8') as json_file:
        json.dump(datagram, json_file, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        # ensure_ascii是解中文编码
        # indent, separators是缩进格式
    with open('tmp.csv','w',errors='ignore',newline='') as f:
        csv_write = csv.writer(f)
        csv_head = ["Name","Title",'School']
        csv_write.writerow(csv_head)
        for i in datagram:
            school_data=i['School']
            for j in i['Teachers']:
                name_data=j['Name']
                title_data=j['Title']
                csv_write.writerow([name_data,title_data,school_data])
    return datagram

# ========= >主程序< =========
s_time = time.time()
soup = getsoup('http://www.sysu.edu.cn/cn/jgsz/yx/index.htm')
data = parse(soup)
t_time = time.time()

print('\n>>Runtime:', format(t_time - s_time, '.2f'), 'Sec')