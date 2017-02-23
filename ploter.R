library(ggplot2)
library(plyr)
#library(grid)


#read collected results
data <- read.csv("summary.csv")

tr_summarized  <- ddply(data,c("vm1r","vm2r","vm1c","vm2c"),summarize, 
                        num = length(rt), 
                        Mean = mean(rt), 
                        std = sd(rt), 
                        se = 2*std/sqrt(num),
                        Thro = mean(thr),
                        u.vm1=mean(uvm1),
                        u.vm2=mean(uvm2),
                        a.vm1=mean(avm1),
                        a.vm2=mean(avm2),
                        q.vm1=mean(qvm1),
                        q.vm2=mean(qvm2),
                        qu.vm1=mean(quvm1),
                        qu.vm2=mean(quvm2)
)


maxRT <- max(tr_summarized$Mean) 
tr_summarized["rtNorm"] <- NA
tr_summarized$rtNorm <- tr_summarized$Mean / maxRT

write.csv(tr_summarized[,c("q.vm1","q.vm2","a.vm1","a.vm2","u.vm1","u.vm2","rtNorm")],"TR_Summarized.csv",row.names=FALSE)

system(command="python server.py",wait=FALSE)
system(command="sleep 40",wait = TRUE)
system(command="python collector.py",wait = FALSE)
system(command="sleep 90",wait = TRUE)

#tr_summarized$qu.vm1 <- tr_summarized$q.vm1 / (1500 * 1000)
#tr_summarized$qu.vm2 <- tr_summarized$q.vm2 / (1500 * 1000)

tr_summarized["sumUsage"] <- NA
tr_summarized["sumActive"] <- NA
tr_summarized["sumQueue"] <- NA
tr_summarized["sumQueueUsage"] <- NA
tr_summarized$sumActive <- tr_summarized$a.vm1 + tr_summarized$a.vm2
tr_summarized$sumQueue <- tr_summarized$q.vm1 + tr_summarized$q.vm2
tr_summarized$sumQueueUsage <- tr_summarized$qu.vm1 + tr_summarized$qu.vm2
tr_summarized$sumUsage <- 1/(1.01-(tr_summarized$u.vm1)) +  1/(1.01-(tr_summarized$u.vm2))


c1 <- 0.01
c2 <- 0.9
c3 <- 0.001
c4 <- -0.8

tr_summarized$g.vm1=1*(c4*(tr_summarized$a.vm1/(1+tr_summarized$q.vm1))+c1*(1/(1.01-(tr_summarized$u.vm1)))+c2*tr_summarized$a.vm1+c3*tr_summarized$qu.vm1)
tr_summarized$g.vm2=1*(c4*(tr_summarized$a.vm2/(1+tr_summarized$q.vm2))+c1*(1/(1.01-(tr_summarized$u.vm2)))+c2*tr_summarized$a.vm2+c3*tr_summarized$qu.vm2)
tr_summarized$g.vm1[tr_summarized$g.vm1 >= 1] <- 1.0
tr_summarized$g.vm2[tr_summarized$g.vm2 >= 1] <- 1.0
tr_summarized$estimated=1*(c4*(tr_summarized$sumActive/(1+tr_summarized$sumQueue))+c1*tr_summarized$sumUsage+c2*tr_summarized$sumActive+c3*tr_summarized$sumQueueUsage) 
tr_summarized$estimated[tr_summarized$estimated >= 1] <- 1.0

m <- ggplot(data = tr_summarized, aes(x=rtNorm, y=estimated)) 
m  + scale_x_continuous(limits=c(0,1),breaks=seq(0, 1, by=0.1)) + 
  scale_y_continuous(limits=c(0,1),breaks=seq(0, 1, by=0.1))+
  theme_bw() +  
  annotate("text", x = 0.455, y = 0.505, label ="R-squared = 0.98", angle = 45, size=9)+
  geom_point(data=tr_summarized,aes(y=(estimated)), size=4, shape=1) +
  xlab("Normalized response time") +ylab("Guiltiness estimative") +
  theme(axis.line.x = element_line(color = 'black'),axis.line.y = element_line(color = 'black'),legend.justification=c(0,1), legend.position=c(0,1),legend.title=element_blank(),axis.text = element_text(size = 24), axis.title = element_text(size = 24),text = element_text(size = 24)) +  
  theme(
    plot.background = element_blank()
    ,panel.border = element_blank()
  ) +
  scale_colour_grey(end=0) +
  geom_abline(intercept = 0)

ggsave("Fig5a.pdf",height=8,width = 8)

#GUILTINESS
p <- ggplot(data=tr_summarized, aes(x=g.vm1, y=g.vm2,fill=Mean,size=Mean))
p +     stat_contour() +
  geom_jitter(position=position_jitter(w=0, h=0),shape=21) +
  scale_fill_gradient2(name="RT",low="white",mid="gray",high="black")+
  geom_tile(aes(fill = Mean)) +
  guides(size=FALSE)+
  scale_x_continuous(limits=c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_size_area(breaks=seq(0,4,by=0.2),max_size=16)+
  xlab(expression(italic(paste("G" [vnf [1]] ))))  +ylab(expression(italic(paste("G" [vnf [2]] )))) +
  theme_bw() +
  theme(legend.text = element_text( size = 16),legend.position=c(0.92,0.85),axis.text = element_text(size = 20), axis.title = element_text(size = 20),text = element_text(size = 20))   

ggsave("Fig3d.pdf",height=6,width = 6)

model <- lm(data=tr_summarized, rtNorm~ (I(tr_summarized$sumUsage)+sumActive+I(1/(1.01-sumQueueUsage))+I((sumActive)/(1+sumQueue)))-1) 
summary(model)

rSquared <- round(summary(model)$r.squared,digits=2)

c1 <- summary(model)$coef[,"Estimate",drop=F][1,1]
c2 <- summary(model)$coef[,"Estimate",drop=F][2,1]
c3 <- summary(model)$coef[,"Estimate",drop=F][3,1]
c4 <- summary(model)$coef[,"Estimate",drop=F][4,1]

tr_summarized$g.vm1=1*(c4*(tr_summarized$a.vm1/(1+tr_summarized$q.vm1))+c1*(1/(1.01-(tr_summarized$u.vm1)))+c2*tr_summarized$a.vm1+c3*tr_summarized$qu.vm1)
tr_summarized$g.vm2=1*(c4*(tr_summarized$a.vm2/(1+tr_summarized$q.vm2))+c1*(1/(1.01-(tr_summarized$u.vm2)))+c2*tr_summarized$a.vm2+c3*tr_summarized$qu.vm2)
tr_summarized$g.vm1[tr_summarized$g.vm1 >= 1] <- 1.0
tr_summarized$g.vm2[tr_summarized$g.vm2 >= 1] <- 1.0
tr_summarized$estimated=1*(c4*(tr_summarized$sumActive/(1+tr_summarized$sumQueue))+c1*tr_summarized$sumUsage+c2*tr_summarized$sumActive+c3*tr_summarized$sumQueueUsage) 
tr_summarized$estimated[tr_summarized$estimated >= 1] <- 1.0

rSquared <- paste("R-squared = ",rSquared)

m <- ggplot(data = tr_summarized, aes(x=rtNorm, y=estimated)) 
m  + scale_x_continuous(limits=c(0,1),breaks=seq(0, 1, by=0.1)) + 
  scale_y_continuous(limits=c(0,1),breaks=seq(0, 1, by=0.1))+
  theme_bw() +  
  annotate("text", x = 0.455, y = 0.505, label =rSquared, angle = 45, size=9)+
  geom_point(data=tr_summarized,aes(y=(estimated)), size=4, shape=1) +
  xlab("Normalized response time") +ylab("Guiltiness estimative") +
  theme(axis.line.x = element_line(color = 'black'),axis.line.y = element_line(color = 'black'),legend.justification=c(0,1), legend.position=c(0,1),legend.title=element_blank(),axis.text = element_text(size = 24), axis.title = element_text(size = 24),text = element_text(size = 24)) +  
  theme(
    plot.background = element_blank()
    ,panel.border = element_blank()
  ) +
  scale_colour_grey(end=0) +
  geom_abline(intercept = 0)

ggsave("Fig5b.pdf",height=8,width = 8)

#GUILTINESS
p <- ggplot(data=tr_summarized, aes(x=g.vm1, y=g.vm2,fill=Mean,size=Mean))
p +     stat_contour() +
  geom_jitter(position=position_jitter(w=0, h=0),shape=21) +
  scale_fill_gradient2(name="RT",low="white",mid="gray",high="black")+
  geom_tile(aes(fill = Mean)) +
  guides(size=FALSE)+
  scale_x_continuous(limits=c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_size_area(breaks=seq(0,4,by=0.2),max_size=16)+
  xlab(expression(italic(paste("G" [vnf [1]] ))))  +ylab(expression(italic(paste("G" [vnf [2]] )))) +
  theme_bw() +
  theme(legend.text = element_text( size = 16),legend.position=c(0.92,0.85),axis.text = element_text(size = 20), axis.title = element_text(size = 20),text = element_text(size = 20))   

ggsave("guiltinessRegression.pdf",height=6,width = 6)

#FROM LEARNING SERVER
learnerCoeff <- read.csv("historic.csv",header=FALSE)
c1 <- learnerCoeff[1,1]
c2 <- learnerCoeff[1,2]
c3 <- learnerCoeff[1,3]
c4 <- learnerCoeff[1,4]

tr_summarized$g.vm1=1*(c4*(tr_summarized$a.vm1/(1+tr_summarized$q.vm1))+c1*(1/(1.01-(tr_summarized$u.vm1)))+c2*tr_summarized$a.vm1+c3*tr_summarized$qu.vm1)
tr_summarized$g.vm2=1*(c4*(tr_summarized$a.vm2/(1+tr_summarized$q.vm2))+c1*(1/(1.01-(tr_summarized$u.vm2)))+c2*tr_summarized$a.vm2+c3*tr_summarized$qu.vm2)
tr_summarized$g.vm1[tr_summarized$g.vm1 >= 1] <- 1.0
tr_summarized$g.vm2[tr_summarized$g.vm2 >= 1] <- 1.0
tr_summarized$estimated=1*(c4*(tr_summarized$sumActive/(1+tr_summarized$sumQueue))+c1*tr_summarized$sumUsage+c2*tr_summarized$sumActive+c3*tr_summarized$sumQueueUsage) 
tr_summarized$estimated[tr_summarized$estimated >= 1] <- 1.0

m <- ggplot(data = tr_summarized, aes(x=rtNorm, y=estimated)) 
m  + scale_x_continuous(limits=c(0,1),breaks=seq(0, 1, by=0.1)) + 
  scale_y_continuous(limits=c(0,1),breaks=seq(0, 1, by=0.1))+
  theme_bw() +  
  annotate("text", x = 0.455, y = 0.505, label ="R-squared = 0.98", angle = 45, size=9)+
  geom_point(data=tr_summarized,aes(y=(estimated)), size=4, shape=1) +
  xlab("Normalized response time") +ylab("Guiltiness estimative") +
  theme(axis.line.x = element_line(color = 'black'),axis.line.y = element_line(color = 'black'),legend.justification=c(0,1), legend.position=c(0,1),legend.title=element_blank(),axis.text = element_text(size = 24), axis.title = element_text(size = 24),text = element_text(size = 24)) +  
  theme(
    plot.background = element_blank()
    ,panel.border = element_blank()
  ) +
  scale_colour_grey(end=0) +
  geom_abline(intercept = 0)

ggsave("learnerCoeff.pdf",height=8,width = 8)


#GUILTINESS
p <- ggplot(data=tr_summarized, aes(x=g.vm1, y=g.vm2,fill=Mean,size=Mean))
p +     stat_contour() +
  geom_jitter(position=position_jitter(w=0, h=0),shape=21) +
  scale_fill_gradient2(name="RT",low="white",mid="gray",high="black")+
  geom_tile(aes(fill = Mean)) +
  guides(size=FALSE)+
  scale_x_continuous(limits=c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_size_area(breaks=seq(0,4,by=0.2),max_size=16)+
  xlab(expression(italic(paste("G" [vnf [1]] ))))  +ylab(expression(italic(paste("G" [vnf [2]] )))) +
  theme_bw() +
  theme(legend.text = element_text( size = 16),legend.position=c(0.92,0.85),axis.text = element_text(size = 20), axis.title = element_text(size = 20),text = element_text(size = 20))   

ggsave("guiltinessLearner.pdf",height=6,width = 6)

#USAGE
p1 <- ggplot(data=tr_summarized, aes(x=u.vm1, y=u.vm2,fill=Mean,size=Mean))
p1 +     stat_contour() +
  geom_jitter(position=position_jitter(w=0, h=0),shape=21) +
  scale_fill_gradient2(name="RT",low="white",mid="gray",high="black")+
  geom_tile(aes(fill = Mean)) +
  guides(size=FALSE)+
  scale_x_continuous(limits=c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_size_area(breaks=seq(0,4,by=0.2),max_size=16)+
  xlab(expression(italic(paste("U" [vnf [1]] ))))  +ylab(expression(italic(paste("U" [vnf [2]] )))) +
  theme_bw() +
  theme(legend.text = element_text( size = 16),legend.position=c(0.92,0.85),axis.text = element_text(size = 20), axis.title = element_text(size = 20),text = element_text(size = 20))   

ggsave("Fig4a.pdf",height=6,width = 6)

#Active
p1 <- ggplot(data=tr_summarized, aes(x=a.vm1, y=a.vm2,fill=Mean,size=Mean))
p1 +     stat_contour() +
  geom_jitter(position=position_jitter(w=0, h=0),shape=21) +
  scale_fill_gradient2(name="RT",low="white",mid="gray",high="black")+
  geom_tile(aes(fill = Mean)) +
  guides(size=FALSE)+
  scale_x_continuous(limits=c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_size_area(breaks=seq(0,4,by=0.2),max_size=16)+
  xlab(expression(italic(paste("A" [vnf [1]] ))))  +ylab(expression(italic(paste("A" [vnf [2]] )))) +
  theme_bw() +
  theme(legend.text = element_text( size = 16),legend.position=c(0.92,0.85),axis.text = element_text(size = 20), axis.title = element_text(size = 20),text = element_text(size = 20))   

ggsave("Fig4b.pdf",height=6,width = 6)

#Queue
p1 <- ggplot(data=tr_summarized, aes(x=qu.vm1, y=qu.vm2,fill=Mean,size=Mean))
p1 +     stat_contour() +
  geom_jitter(position=position_jitter(w=0, h=0),shape=21) +
  scale_fill_gradient2(name="RT",low="white",mid="gray",high="black")+
  geom_tile(aes(fill = Mean)) +
  guides(size=FALSE)+
  scale_x_continuous(limits=c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.1)) +
  scale_size_area(breaks=seq(0,4,by=0.2),max_size=16)+
  xlab(expression(italic(paste("Qu" [vnf [1]] ))))  +ylab(expression(italic(paste("Qu" [vnf [2]] )))) +
  theme_bw() +
  theme(legend.text = element_text( size = 16),legend.position=c(0.92,0.85),axis.text = element_text(size = 20), axis.title = element_text(size = 20),text = element_text(size = 20))   

ggsave("Fig4c.pdf",height=6,width = 6)
