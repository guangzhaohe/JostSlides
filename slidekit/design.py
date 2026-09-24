"""Shared 1152 × 648 layouts, large typography and palette."""
PAPER='F6F4EF'; INK='172E35'; MUTED='52676B'; WHITE='FFFFFF'; TEAL='B8E3D1'; BLUE='315BD6'; MINT='E0EBE5'; PALE_BLUE='E6EBF7'; DARK_PANEL='244149'; LINE='C8D3CE'
def t(x,y,content,size=32,bold=False,color=INK,width=1024):
    return (x,y,width,size*1.3,content,size,bold,color)
def lines(x,y,content,size=32,bold=False,color=INK,width=1024,leading=None):
    return [t(x,y+i*(leading or size*1.3),v,size,bold,color,width) for i,v in enumerate(content)]
def slide(id,name,text,rects=(),notes='',bg=PAPER,**extra):
    return dict(id=id,name=name,text=text,rects=list(rects),notes=notes,bg=bg,**extra)
