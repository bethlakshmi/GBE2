ALTER TABLE `gbe_lightinginfo2` ADD `costume` LONGTEXT NOT NULL ; 
CREATE TABLE IF NOT EXISTS `gbe_cueinfo` (\
  `id` int(11) NOT NULL AUTO_INCREMENT,\
  `cue_sequence` int(10) unsigned NOT NULL,\
  `cue_off_of` longtext NOT NULL,\
  `follow_spot` varchar(25) NOT NULL,\
  `center_spot` varchar(20) NOT NULL,\
  `backlight` varchar(20) NOT NULL,\
  `cyc_color` varchar(25) NOT NULL,\
  `wash` varchar(25) NOT NULL,\
  `sound_note` longtext NOT NULL,\
  `techinfo_id` int(11) NOT NULL,\
  PRIMARY KEY (`id`),\
  KEY `gbe_cueinfo_86f7e5a4` (`techinfo_id`)\
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;\
\
--\
-- Constraints for dumped tables\
--\
\
--\
-- Constraints for table `gbe_cueinfo`\
--\
ALTER TABLE `gbe_cueinfo`\
  ADD CONSTRAINT `techinfo_id_refs_id_7159f105` FOREIGN KEY (`techinfo_id`) REFERENCES `gbe_techinfo` (`id`);\
\
\
}