import math
from language_manager import lang_manager

def get_EandG_vaule(fc):
    Ec=12000*math.sqrt(fc)/1000 #tf/cm2
    ShearM=Ec/2/(1+0.25)
    return Ec,ShearM

def steel_material_info(keyin):
    #[fy,fu, ?] unit:tf/cm2
    chart={'A36': [2.5,4.2,4.9], 'A572': [3.3,4.9,4.9],'SN490': [3.3,4.9,4.9],'SM570M': [4.2,5.7,5.6]}
    result=chart.get(keyin,'none')
    fy=result[0]
    fu=result[1]
    return fy,fu

def rebar_info(keyin):
    chart={'#3(D10)': 0.953, '#4(D13)': 1.27,'#5(D16)': 1.588,'#6(D19)': 1.905,
            '#7(D22)': 2.223, '#8(D25)': 2.54,'#9(D29)': 2.865,'#10(D32)': 3.226,'#11(D36)': 3.581}
    rebar_d=chart.get(keyin,'none')
    if rebar_d == 'none':
        return 'none', 'none'
    Ab=math.pi*rebar_d**2/4
    return rebar_d, Ab

def stirrup_info(keyin):
    chart={
        # Chinese
        '雙肢箍': 2, 
        '三肢箍': 3,
        '四肢箍': 4,
        # English
        'Two-leg Stirrup': 2,
        'Three-leg Stirrup': 3, 
        'Four-leg Stirrup': 4,
        # Thai
        'เหล็กปลอกสองขา': 2,
        'เหล็กปลอกสามขา': 3,
        'เหล็กปลอกสี่ขา': 4
    }
    result = chart.get(keyin, 2)  # Default to 2 if not found
    return result

def get_clear_cover(keyin):
    chart={'Beam': 4, 'Column': 4,'Slab': 2} #cm
    result = chart.get(keyin, 4)  # Default to 4 if not found
    return result


def cal_bar_allowable_num(B,PrtctT,rebar_d,stirrup_d,cnstrctblty,type) :
    if type=='Beam' :
        cleardb_h=1.5*max(2.5,rebar_d) if cnstrctblty=='yes' else  max(2.5,rebar_d)
    elif type=='Column' :
        cleardb_h=1.5*max(4,1.5*rebar_d) if cnstrctblty=='yes' else  max(4,1.5*rebar_d)
    RebarAllowabelNumPerRow=max(0,math.floor((B-PrtctT*2-stirrup_d*2-rebar_d)/(rebar_d+cleardb_h))+1)
    return RebarAllowabelNumPerRow,cleardb_h


def bar_allowable_num_clicked(data,type):
    try :
        PrtctT=get_clear_cover(type)
        data.barallowtext.setText('')
        B=float(data.width.text())
        barchart=['#3(D10)', '#4(D13)','#5(D16)','#6(D19)','#7(D22)', '#8(D25)','#9(D29)','#10(D32)','#11(D36)']
        cnstrctblty=data.cnstrctblty
        BarAllowNum=[]
        for i in barchart:
            rebar_d, Ab=rebar_info(i)
            RebarAllowabelNumPerRow,cleardb_h=cal_bar_allowable_num(B,PrtctT,rebar_d,1.588,cnstrctblty,type)
            BarAllowNum.append(str(RebarAllowabelNumPerRow))
        for i in range(len(barchart)):
            data.barallowtext.append(barchart[i]+lang_manager.tr('results.single_row_capacity')+' :'+BarAllowNum[i]+lang_manager.tr('results.bars'))
    except :
        data.barallowtext.setText('Please input the section width')

def arrange_rebar(RebarNum,BarAllowabelNumPerRow):
    if RebarNum<=BarAllowabelNumPerRow :
        arrange=1
    elif RebarNum<=2*BarAllowabelNumPerRow :
        arrange=2
    else :
        arrange='超過限制'
    return arrange

def get_beta(fc):
    beta=0.85 if fc <= 280  else max(0.65,0.85-0.05/70*(fc-280))
    return beta

def cal_d_eff(B,D,PrtctT,rebar_d,stirrup_d,RebarNum,cnstrctblty,type):
    RebarAllowabelNumPerRow,cleardb_h=cal_bar_allowable_num(B,PrtctT,rebar_d,stirrup_d,cnstrctblty,type)
    arrange=arrange_rebar(RebarNum,RebarAllowabelNumPerRow)
    if arrange == 1 :
        d=D-PrtctT-stirrup_d-rebar_d/2
        dt=d
    else :
        d0=D-PrtctT-stirrup_d-rebar_d/2
        total=(RebarNum-(arrange-1)*RebarAllowabelNumPerRow)*(d0-(arrange-1)*(cleardb_h+rebar_d))
        for i in range(arrange-1) :
            total+=(d0-i*cleardb_h)*RebarAllowabelNumPerRow
        d=total/RebarNum
        dt=d0
    return d,dt,RebarAllowabelNumPerRow

def get_section_info(B,D,fc,fy,bar1,bar2,tensilebar_num,compressionbar_num,stirrup_size,PrtctT,cnstrctblty,type):
    beta=get_beta(fc)
    Ec,ShearM=get_EandG_vaule(fc)
    [db_rebar1,Ab_rebar1]=rebar_info(bar1)
    [db_rebar2,Ab_rebar2]=rebar_info(bar2)
    [db_stirrup,Ab_stirrup]=rebar_info(stirrup_size)
    As=tensilebar_num*Ab_rebar1
    Ass=compressionbar_num*Ab_rebar2
    [d,dt,RebarAllowabelNumPerRow1]=cal_d_eff(B,D,PrtctT,db_rebar1,db_stirrup,tensilebar_num,cnstrctblty,type)
    [dd0,ddt,RebarAllowabelNumPerRow2]=cal_d_eff(B,D,PrtctT,db_rebar2,db_stirrup,compressionbar_num,cnstrctblty,type)
    dd=D-dd0
    return beta,Ec,db_rebar1,Ab_rebar1,db_rebar2,Ab_rebar2,As,Ass,d,dt,dd,db_stirrup,Ab_stirrup,RebarAllowabelNumPerRow1,RebarAllowabelNumPerRow2

def cal_effectived_beta(arrange,D,PrtctT,bard1,bard2,fc,stirrup_d,BarNum,BarAllowNumPerRow) :
    #計算有效深度
    if arrange[0] == lang_manager.tr('results.single_row') or BarNum[0] == 0:
        d=D-PrtctT-stirrup_d-bard1/2
        dt=d
    else: #僅考慮兩排的情況
        d1=D-PrtctT-stirrup_d-bard1/2
        delta=2.5+bard1
        row=int(BarNum[0]//BarAllowNumPerRow[0]+1)
        d=(BarNum[0]%BarAllowNumPerRow[0])*(d1-(row-1)*delta)/BarNum[0]
        # print(BarNum[0]%BarAllowNumPerRow[0])
        for i in range(row-1) :
            d+=BarAllowNumPerRow[0]/BarNum[0]*(d1-i*delta)
        dt=d1
    if arrange[1] == lang_manager.tr('results.single_row') or BarNum[1] == 0:
        dd=PrtctT+stirrup_d+bard2/2
    else:
        dd1=PrtctT+stirrup_d+bard2/2
        delta=2.5+bard2
        row=int(BarNum[1]/BarAllowNumPerRow[1]+1)
        print(row)
        dd=(BarNum[1]%BarAllowNumPerRow[1])*(dd1+(row-1)*delta)/BarNum[1]
        print(dd)
        for i in range(row-1) :
            dd+=BarAllowNumPerRow[1]/BarNum[1]*(dd1+i*delta)
            print(dd)
    #計算beta1值
    beta=get_beta(fc)
    return d,dt,dd,beta

def cal_phi(c,d,dt):
    #計算phi值
    es=0.003/c*(d-c)
    et=0.003/c*(dt-c)
    phi=min(0.9,0.65+0.25/0.003*(et-0.002)) if et>=0.002 else 0.65
    if et>=0.005 :
        result1=lang_manager.tr('results.tension_control')
    elif et>=0.002 :
        result1=lang_manager.tr('results.transition')
    else:
        result1=lang_manager.tr('results.compression_control')
    if et>=0.004 :
        result2=lang_manager.tr('results.strain_satisfies')
    else:
        result2=lang_manager.tr('results.strain_not_satisfies')
    return es,et,result1,result2,phi

def cal_shear_strngth(stirrup_d,stirrup_num,stirrup_span,fc,fy,B,d) :
    #無軸壓
    Vc=0.53*fc**0.5*B*d/1000 #tf
    Av=stirrup_num*math.pi*stirrup_d**2/4 #cm2
    Vs=Av/stirrup_span*fy*d/1000 #tf
    phiVn=0.75*(Vc+Vs) #tf
    return Av,Vc,phiVn

def check_stirrup_span_limit(Vu,Vc,fc,fy,B,d,Av) :
    # ตาม ACI 9.7.6.2.2 Maximum spacing of legs of shear reinforcement
    # Required Vs = Vu/φ - Vc
    phi_v = 0.75  # reduction factor for shear
    Vs_required = Vu/phi_v - Vc  # กำลังเฉือนที่ต้องการจากเหล็กปลอก
    
    if Vu <= 0.5*phi_v*Vc :  # 0.5φVc
        s_max=['no need for stirrup']
        s_max1 = 'no need'
        s_max2 = 'no need'
    elif Vs_required <= 0.33*(fc**0.5)*B*d/1000 :  # 0.33√f'c*b*d (tf)
        # ระยะห่างสูงสุด = d/2 หรือ 600 มม.
        s_max1_calc = 600  # mm ตามมาตรฐาน
        s_max2_calc = d/2*10  # d/2 (cm to mm)
        s_max_calc = min(s_max1_calc, s_max2_calc)
        s_max=[str(int(s_max_calc))]
        s_max1 = str(int(s_max1_calc))
        s_max2 = str(int(s_max2_calc))
    else :  # Vs > 0.33√f'c*b*d
        # ระยะห่างสูงสุด = d/4 หรือ 300 มม.
        s_max1_calc = 300  # mm ตามมาตรฐาน
        s_max2_calc = d/4*10  # d/4 (cm to mm)
        s_max_calc = min(s_max1_calc, s_max2_calc)
        s_max=[str(int(s_max_calc))]
        s_max1 = str(int(s_max1_calc))
        s_max2 = str(int(s_max2_calc))
    
    return s_max, s_max1, s_max2

#////////////////// For   矩形梁///////////////////////////
def cal_recbeam_Mn(dd,fc,beta,B,d,fy,Ass,As) :
    cy=3*dd
    Asy=0.85*fc*beta*cy*B/fy+Ass*(fy-0.85*fc)/fy #壓筋降伏時對應的拉力鋼筋量
    if As >=Asy : #壓筋降伏
        a=(As*fy-Ass*(fy-0.85*fc))/(0.85*fc*B)
        c=a/beta
        Cc=0.85*fc*beta*B*c
        Cs=Ass*(fy-0.85*fc)
        es=0.003/c*(d-c)
        result0=lang_manager.tr('results.compression_yielding_tension_yielding') if es > 0.002 else lang_manager.tr('results.compression_yielding_tension_not_yielding')
    else: #壓筋不降伏
        result0=lang_manager.tr('results.compression_not_yielding')
        c=max(math2(0.85*fc*beta*B,(6120-0.85*fc)*Ass-As*fy,-6120*dd*Ass))
        a=beta*c
        fs=6120/c*(c-dd)
        Cc=0.85*fc*beta*B*c
        Cs=Ass*(fs-0.85*fc)
    Mn=(Cc*(d-0.5*a)+Cs*(d-dd))/100000
    return Asy,result0,c,Cc,Cs,Mn



#///////////////////////For T型梁////////////////////////
#計算有效翼寬
def cal_effective_width(BeamCondition,B,Sn,hf,length) :
    # Check beam condition for all languages
    is_interior_beam = (BeamCondition in [
        lang_manager.tr("beam.interior_beam"),  # Current language
        "內梁",  # Chinese
        "คานใน",  # Thai  
        "Interior Beam"  # English
    ])
    
    if is_interior_beam:
        be=min(length/4,B+Sn,B+16*hf)
    else :
        be=min(B+length/12,B+Sn/2,B+6*hf)
    return be

#計算彎矩強度
def cal_tbeam_Mn(dd,beta,hf,fc,fy,B,d,be,Ass,As) :
    #計算臨界斷面的拉力鋼筋量(c=hf的情況下拉筋需降伏的臨界鋼筋量)
    Ccritical=hf/beta
    fsscritical=6120/Ccritical*(Ccritical-dd)
    Ascritical=0.85*fc/fy*be*hf+Ass*(fsscritical-0.85*fc)/fc
    cy=3*dd
    if beta*cy>hf :
        Asy=0.85*fc/fy*(hf*be+B*(beta*cy-hf))+Ass*(fy-0.85*fc)/fy #壓筋降伏時對應的拉力鋼筋量
    else :
        Asy=0.85*fc*beta*cy*B/fy+Ass*(fy-0.85*fc)/fy #壓筋降伏時對應的拉力鋼筋量
    if As >=Asy : #壓筋降伏
        if As > Ascritical : #T型
            Ac=(As*fy-Ass*(fy-0.85*fc))/(0.85*fc)
            a=(Ac-hf*be+hf*B)/B
            c=a/beta
            Cc=0.85*fc*Ac
            Cs=Ass*(fy-0.85*fc)
            es=0.003/c*(d-c)
            if es > 0.002 :
                result0=lang_manager.tr('results.compression_area_t_shape') + '\n' + lang_manager.tr('results.compression_yielding_tension_yielding')
            else:
                result0=lang_manager.tr('results.compression_area_t_shape') + '\n' + lang_manager.tr('results.compression_yielding_tension_not_yielding')
        else : #矩形
            a=(As*fy-Ass*(fy-0.85*fc))/(0.85*fc*be)
            c=a/beta
            Cc=0.85*fc*beta*be*c
            Cs=Ass*(fy-0.85*fc)
            es=0.003/c*(d-c)
            if es > 0.002 :
                result0=lang_manager.tr('results.compression_area_rectangular') + '\n' + lang_manager.tr('results.compression_yielding_tension_yielding')
            else:
                result0=lang_manager.tr('results.compression_area_rectangular') + '\n' + lang_manager.tr('results.compression_yielding_tension_not_yielding')
    else: #壓筋不降伏
        if As > Ascritical : #T型 :
            result0=lang_manager.tr('results.compression_area_t_shape') + '\n' + lang_manager.tr('results.compression_not_yielding')
            c=max(math2(0.85*fc*beta*B,(6120-0.85*fc)*Ass-As*fy+0.85*fc*(be-B)*hf,-6120*dd*Ass))
            a=beta*c
            fs=6120/c*(c-dd)
            Ac=be*hf+(a-hf)*B
            Cc=0.85*fc*Ac
            Cs=Ass*(fs-0.85*fc)
        else : #矩形
            result0=lang_manager.tr('results.compression_area_rectangular') + '\n' + lang_manager.tr('results.compression_not_yielding')
            c=max(math2(0.85*fc*beta*be,(6120-0.85*fc)*Ass-As*fy,-6120*dd*Ass))
            a=beta*c
            fs=6120/c*(c-dd)
            Cc=0.85*fc*beta*be*c
            Cs=Ass*(fs-0.85*fc)
    Mn=(Cc*(d-0.5*a)+Cs*(d-dd))/100000
    return Asy,result0,c,Cc,Cs,Mn



def math2(matha,mathb,mathc):
        q=mathb**2-4*matha*mathc
        if q<0:
            output="Your equation has no root."
        elif q==0:
            output = -mathb / (2 * matha)
        else:
            q1=(-mathb+q**0.5)/(2*matha)
            q2=(-mathb-q**0.5)/(2*matha)
            output=[q1, q2]
        return output 