class MyClass
{
    public static void main(String []args)
    {
        String a []= {
            "a = 
            b = 
            c = 
            d = "
        };
        String b []= {
            "1",
            "2",
            "3",
            "4"
        };
        if (a.length==b.length)
        {
            for (int i=0;i<a.length;i++)
            {
                a[i] = a[i]+b[i];
            }
        }
        for (int i=0;i<a.length;i++)
            System.out.println(a[i]);
}
}
