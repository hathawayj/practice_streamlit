##### Temple Dates and Square Footage
##### 
# http://bradleyboehmke.github.io/2015/12/scraping-html-tables.html
# https://stackoverflow.com/questions/23699271/force-character-vector-encoding-from-unknown-to-utf-8-in-r
# https://selectorgadget.com/

pacman::p_load(tidyverse, sf, ggrepel, downloader, ggmap, rvest, lubridate, RcppRoll)

temple_locs <- read_csv("https://churchofjesuschristtemples.org/maps/gps/", locale = locale(encoding = "latin1"))
#temple_geometry <- st_read("https://churchofjesuschristtemples.org/maps/kml/timeline/")
temple_size <- "https://churchofjesuschristtemples.org/statistics/dimensions/" %>% read_html() %>% html_nodes("table") %>% html_table() %>% .[[1]]
temple_time <- "https://churchofjesuschristtemples.org/statistics/milestones/" %>% read_html() %>% html_nodes("table") %>% html_table() %>% .[[2]]
# url_distance <- "https://churchofjesuschristtemples.org/statistics/distances/" %>% read_html() %>% html_nodes("table") %>% html_table() 

dat_annot <- tibble(date = c("1973-01-01", "1981-07-23", "1982-12-2", "1985-11-10", "1994-06-05", "1995-03-12", "1997-6-6", "2008-02-03"), 
                    event_short = c("Chair of Temple Committee", "3rd Counselor: SW Kimball", "2nd Counselor: SW Kimball", "1st Counselor: ET Benson", "1st Counselor: HW Hunter", "President and Prophet", "Juarez Revelation on Small Temples", "Death") %>% factor(levels = c("Chair of Temple Committee", "3rd Counselor: SW Kimball", "2nd Counselor: SW Kimball", "1st Counselor: ET Benson", "1st Counselor: HW Hunter", "President and Prophet", "Juarez Revelation on Small Temples", "Death")), 
                    event_long = c('In 1973, while serving as chairman of the Church’s Temple Committee, he wrote in his journal: “The Church could build [many smaller] temples for the cost of the Washington Temple [then under construction]. It would take the temples to the people instead of having the people travel great distances to get to them.”', 
                                   'Called as an additional Counselor to President Spencer W. Kimball to assist the President and his two counselors.', 
                                   'Called as Second Counselor in the First Presidency.', 
                                   'Called as First Counselor to President Ezra Taft Benson.',
                                   'Called as First Counselor to President Howard W. Hunter.',
                                   'Ordained and Set Apart as President of the Church.',
                                   'There came to my mind an idea I’d never thought of before. It was inspired of the Lord to build a temple there, a small one, very small, six thousand square feet with facilities.',
                                   'Died in Salt Lake City, Utah.'), 
                    event_reference = c("https://www.lds.org/manual/teachings-of-presidents-of-the-church-gordon-b-hinckley/the-life-and-ministry-of-gordon-b-hinckley?lang=eng", rep("https://history.lds.org/timeline/gordon-b-hinckley?lang=eng", 5), "https://rsc.byu.edu/archived/colonia-ju-rez-temple-prophet-s-inspiration/president-hickleys-inspiration", "https://history.lds.org/timeline/gordon-b-hinckley?lang=eng"),
                    y_lab = c(250000, 235000, 220000, 205000, 190000, 165000, 150000, 135000 ))


dimensions <- temple_size %>%
  as_tibble() %>%
  select_all("str_trim","both") %>%
  mutate(SquareFootage = parse_number(SquareFootage))
  
times <- temple_time %>% 
  as_tibble() %>%
  mutate(Announcement = dmy(Announcement), Groundbreaking = dmy(Groundbreaking), Dedication = dmy(Dedication))

dat <- temple_locs %>% 
  full_join(dimensions) %>% 
  full_join(times) %>% 
  arrange(Groundbreaking) %>%
  mutate(US = ifelse(Country == "United States", TRUE, FALSE))
  

write_rds(dat, "scripts/templdat.rds")


## Now make the plots
## 


dat <- read_rds("scripts/templdat.rds")

(plot <- dat %>%
  ggplot(aes(x = Announcement, y = SquareFootage)) +
  geom_point() +
  geom_smooth(alpha = .05, span = .65) +
  scale_x_date(date_breaks = "15 years", date_labels = "%b-%Y", date_minor_breaks = "5 years"))

plot +  
  scale_x_date(date_breaks = "2 years", date_labels = "%b-%Y", date_minor_breaks = "1 years") +
  coord_cartesian(xlim = as.Date(c("1979-01-01", "2015-01-01")))

p <- plot + 
  geom_vline(data = dat_annot, aes(xintercept = date(date), color = event_short), size = 1.1) +
  geom_point(data = filter(dat, Temple == "Washington D.C. Temple"), color = "red", size = 2.5, shape = 15 ) +
  labs(x = "Date of temple announcement", y = "Temple square footage", title = "Sizes of temples over time", 
       subtitle = "vertical lines mark historical events of President Hinckley", color = "Hinckley\nTimeline") +
  theme_bw() +
  theme(legend.position = "bottom") +
  guides(color = guide_legend(override.aes = list(size = 3), nrow = 2, byrow = TRUE )) +
  scale_color_brewer(type = "qual") +
  scale_y_continuous(labels = scales::comma, breaks = c(seq(0, 250000, by = 25000))) +
  theme(panel.grid.minor.y = element_blank())

p + 
  geom_text_repel(data = filter(dat, Announcement < "1975-01-01" | SquareFootage > 75000), aes(label = gsub("Temple", "", Temple))) + 
  geom_text_repel(data = filter(dat, SquareFootage < 10500), aes(label = gsub("Temple", "", Temple)))
  

ggsave("docs/images/temples.png", width = 14, height = 8)

p + 
  coord_cartesian(xlim = as.Date(c("1973-01-01", "2015-01-01")), ylim = c(0, 145000)) +
  geom_label_repel(data = filter(dat, Announcement > "1975-01-01" & SquareFootage > 75000), aes(label = gsub("Temple", "", Temple)))  +
  geom_label_repel(data = filter(dat, Announcement > "1975-01-01" & SquareFootage < 10000), aes(label = gsub("Temple", "", Temple)), 
                  nudge_x = -30, min.segment.length = unit(.01, "mm"))  +
  scale_x_date(date_breaks = "2 years", date_labels = "%Y", date_minor_breaks = "1 years") 
  

ggsave("docs/images/temples_zoom.png", width = 14, height = 8)

  


