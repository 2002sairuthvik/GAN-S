import torch
import torch.nn as nn

class Block(nn.Module):
    def __init__(self,in_channels,out_channels,down=True,act='relu',use_dropout=False):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels,out_channels,4,2,1,bias=False,padding_mode="reflect")
            if down  # till here we are taking the u-net encoder architecture trying to to reflect same but not use conv layers as many as they've used in u-net
            else nn.ConvTranspose2d(in_channels,out_channels,4,2,1,bias=False), # here comes the decoder part of the u-net model
            nn.BatchNorm2d(out_channels),
            nn.ReLU() if act=="relu" else nn.LeakyReLU(0.2),
        )
        self.use_dropout = use_dropout
        self.dropout = nn.Dropout(0.5)
        
    def forward(self,x):
        x = self.conv(x)
        return self.dropout(x) if self.use_dropout else x
    
class Generator(nn.Module):
    def __init__(self,in_channels=3, features=64):
        super().__init__()
        self.initial_down = nn.Sequential(
            nn.Conv2d(in_channels,features,4,2,1,padding_mode="reflect"),
            nn.LeakyReLU(0.2),
            
        )#128
        
        self.down1 = Block(features, features*2,down=True,act='leaky',use_dropout=False) #64
        self.down2 = Block(features*2, features*4,down=True,act='leaky',use_dropout=False)#32
        self.down3 = Block(features*4, features*8,down=True,act='leaky',use_dropout=False)#16
        self.down4 = Block(features*8, features*8,down=True,act='leaky',use_dropout=False)#8
        self.down5 = Block(features*8, features*8,down=True,act='leaky',use_dropout=False)#4
        self.down6 = Block(features*8, features*8,down=True,act='leaky',use_dropout=False)#2
        self.bottleneck = nn.Sequential(
            nn.Conv2d(features*8,features*8,4,2,1,padding_mode='reflect'),
            nn.ReLU()
            ) # 1x1
        self.up1 = Block(features*8,features*8,down=False,act="relu",use_dropout=True) 
        self.up2 = Block(features*8*2,features*8,down=False,act="relu",use_dropout=True) # so basically from here why there is features*8*2 is we adding the skip connection from above similar to same conv so but the out channels it make conv learn all those give only required out channels not combination of both so thats why the out channels = features*8
        self.up3 = Block(features*8*2,features*8,down=False,act="relu",use_dropout=True)
        self.up4 = Block(features*8*2,features*8,down=False,act="relu",use_dropout=False)
        self.up5 = Block(features*8*2,features*4,down=False,act="relu",use_dropout=False)
        self.up6 = Block(features*4*2,features*2,down=False,act="relu",use_dropout=False)
        self.up7 = Block(features*2*2,features,down=False,act="relu",use_dropout=False)
        self.final_up = nn.Sequential(
            nn.Conv2d(features*2,in_channels,kernel_size=4,stride=2,padding=1),
            nn.Tanh()
        )
        
    def forward(self,x):
        d1 = self.initial_down(x)
        d2 = self.down1(d1)
        d3 = self.down2(d2)
        d4 = self.down3(d3)
        d5 = self.down4(d4)
        d6 = self.down5(d5)
        d7 = self.down6(d6)
        bottleneck = self.bottleneck(d7)
        up1 = self.up1(bottleneck)       
        up2 = self.up2(torch.cat([up1,d7],1))
        up3 = self.up3(torch.cat([up2,d6],1)) 
        up4 = self.up4(torch.cat([up3,d5],1)) 
        up5 = self.up5(torch.cat([up4,d4],1))  
        up6 = self.up6(torch.cat([up5,d3],1)) 
        up7 = self.up7(torch.cat([up6,d2],1))
        return self.final_up(torch.cat([up7,d1],1))
    
    
    
def test():
    x = torch.randn((1,3,256,256))
    model = Generator(in_channels=3,features=64)
    preds = model(x)
    print(preds.shape)
    
    
if __name__ == "__main__":
    test() 

        