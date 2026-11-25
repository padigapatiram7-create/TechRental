import { useEffect, useState } from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import { FiSearch, FiShoppingCart, FiUser, FiLogOut, FiTrash2 } from 'react-icons/fi'
import { apiFetch, clearTokens, getRefreshToken, saveTokens } from './api'
import './App.css'

function Header({ user, logout }) {
  return <header><Link className="brand" to="/">Tech<span>Rentals</span></Link><nav><Link to="/gadgets">Browse</Link>{user && <Link to="/cart"><FiShoppingCart /> Cart</Link>}{user?.user_type === 'lender' && <Link to="/lender/dashboard">Lender</Link>}{user && <Link to="/orders">My Orders</Link>}<button className="nav-button" onClick={user ? logout : () => {}}>{user ? <><FiLogOut /> {user.username}</> : <Link to="/login"><FiUser /> Sign in</Link>}</button></nav></header>
}

function Card({ g }) {
  return <Link className="gadget-card" to={`/gadgets/${g.id}`}><img src={g.imageUrl || g.image_url} alt={g.title} />{g.is_premium && <b className="premium-badge">Premium</b>}<div className="card-copy"><small>{g.brand} · {g.category}</small><h3>{g.title}</h3><p><strong>₹{Number(g.price).toLocaleString('en-IN')}</strong> / day</p><span>Deposit ₹{Number(g.deposit).toLocaleString('en-IN')}</span></div></Link>
}

function Gadgets() {
  const [data, setData] = useState({ results: [], count: 0 })
  const [premium, setPremium] = useState([])
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const [brand, setBrand] = useState('')
  const [rating, setRating] = useState('')
  const [ordering, setOrdering] = useState('')
  const [typed, setTyped] = useState('')
  const [search, setSearch] = useState('')
  useEffect(() => {
    const p = new URLSearchParams({ page, page_size: 5 })
    if (category) p.set('category', category)
    if (brand) p.set('brand', brand)
    if (rating) p.set('rating', rating)
    if (ordering) p.set('ordering', ordering)
    if (search) p.set('search', search)
    apiFetch(`/api/gadgets/?${p}`).then(r => r.ok && setData(r.data))
  }, [page, category, brand, rating, ordering, search])
  useEffect(() => { apiFetch('/api/gadgets/?is_premium=true&page_size=6').then(r => r.ok && setPremium(r.data.results || [])) }, [])
  return <main className="page"><section className="hero-panel"><div><small>GEAR FOR EVERY STORY</small><h1>Rent tech.<br />Create more.</h1><p>Professional cameras, gaming gear, laptops and drones.</p></div><div className="premium-strip"><h2>Premium picks</h2>{premium.length ? premium.slice(0, 3).map(g => <Card g={g} key={g.id} />) : <p>Sign in to unlock premium gadgets.</p>}</div></section><div className="catalog-layout"><aside className="filters"><h2>Filters</h2>{['Cameras','Consoles','Laptops','Drones','Projectors'].map(v => <button className={category === v ? 'active' : ''} onClick={() => {setPage(1); setCategory(category === v ? '' : v)}} key={v}>{v}</button>)}<label>Brand<select value={brand} onChange={e => {setPage(1); setBrand(e.target.value)}}><option value="">All brands</option><option>Sony</option><option>DJI</option><option>Dell</option><option>GoPro</option><option>Epson</option></select></label><label>Minimum rating<select value={rating} onChange={e => {setPage(1); setRating(e.target.value)}}><option value="">Any rating</option><option value="4">4+</option><option value="4.5">4.5+</option></select></label></aside><section className="catalog"><form className="search-row" onSubmit={e => {e.preventDefault(); setPage(1); setSearch(typed)}}><FiSearch /><input value={typed} onChange={e => setTyped(e.target.value)} placeholder="Search title or brand" /><button>Search</button></form><div className="catalog-toolbar"><p>{data.count} gadgets</p><select value={ordering} onChange={e => setOrdering(e.target.value)}><option value="">Recommended</option><option value="price">Price Low-High</option><option value="-price">Price High-Low</option></select></div><div className="gadget-grid">{data.results.map(g => <Card g={g} key={g.id} />)}</div>{!data.results.length && <div className="empty-state">No gadgets found.</div>}<div className="pagination"><button disabled={!data.previous} onClick={() => setPage(p => p - 1)}>Previous</button><span>Page {page}</span><button disabled={!data.next} onClick={() => setPage(p => p + 1)}>Next</button></div></section></div></main>
}

function Detail({ user }) {
  const { id } = useParams(), navigate = useNavigate()
  const [g, setG] = useState(null), [days, setDays] = useState(1), [error, setError] = useState('')
  useEffect(() => { apiFetch(`/api/gadgets/${id}/`).then(r => r.ok ? setG(r.data) : setError(r.data.detail || 'Unable to load gadget')) }, [id])
  const add = async () => {
    if (!user) return navigate('/login')
    const r = await apiFetch('/api/cart/add/', {method:'POST', body:JSON.stringify({gadget:Number(id), quantity:days})})
    if (r.ok) navigate('/cart'); else setError(r.data.detail)
  }
  if (error) return <main className="page empty-state">{error}</main>
  if (!g) return <main className="page">Loading…</main>
  return <main className="page detail-page"><img src={g.imageUrl} alt={g.title} /><section><small>{g.brand} · {g.category}</small><h1>{g.title}</h1><p>{g.description}</p><dl><dt>Daily price</dt><dd>₹{Number(g.price).toLocaleString('en-IN')}</dd><dt>Refundable deposit</dt><dd>₹{Number(g.deposit).toLocaleString('en-IN')}</dd><dt>In the box</dt><dd>{g.in_the_box}</dd></dl><label>Rental days<input type="number" min="1" value={days} onChange={e=>setDays(Number(e.target.value))}/></label><strong className="detail-total">Total ₹{(Number(g.price)*days).toLocaleString('en-IN')}</strong><button className="primary" onClick={add}>ADD TO CART</button></section></main>
}

function Login({ onLogin }) {
  const navigate = useNavigate()
  const [form,setForm]=useState({username:'',password:''}), [error,setError]=useState('')
  const submit=async e=>{e.preventDefault(); const r=await apiFetch('/api/users/login/',{method:'POST',body:JSON.stringify(form)}); if(r.ok){saveTokens(r.data); onLogin(r.data); navigate(r.data.user_type==='lender'?'/lender/dashboard':'/gadgets')}else setError(r.data.detail||'Login failed')}
  return <main className="auth-page"><form className="auth-card" onSubmit={submit}><small>WELCOME BACK</small><h1>Sign in</h1>{error&&<p className="error">{error}</p>}<label>Username<input value={form.username} onChange={e=>setForm({...form,username:e.target.value})}/></label><label>Password<input type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label><button className="primary">Sign in</button><p>New here? <Link to="/register">Create account</Link></p></form></main>
}

function Register() {
  const navigate=useNavigate()
  const [form,setForm]=useState({username:'',email:'',password:'',confirm:'',user_type:'renter'}),[error,setError]=useState('')
  const submit=async e=>{e.preventDefault(); if(form.password!==form.confirm)return setError('Passwords do not match'); const r=await apiFetch('/api/users/register/',{method:'POST',body:JSON.stringify({username:form.username,email:form.email,password:form.password,user_type:form.user_type})}); if(r.ok)navigate('/login');else setError(r.data.detail||Object.entries(r.data).map(([k,v])=>`${k}: ${Array.isArray(v)?v.join(' '):v}`).join(' '))}
  return <main className="auth-page"><form className="auth-card" onSubmit={submit}><small>JOIN TECHRENTALS</small><h1>Create account</h1>{error&&<p className="error">{error}</p>}<label>Username<input value={form.username} onChange={e=>setForm({...form,username:e.target.value})}/></label><label>Email<input value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label><label>Password<input type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label><label>Confirm password<input type="password" value={form.confirm} onChange={e=>setForm({...form,confirm:e.target.value})}/></label><label>Account type<select value={form.user_type} onChange={e=>setForm({...form,user_type:e.target.value})}><option value="renter">Renter</option><option value="lender">Lender</option></select></label><button className="primary">Create account</button></form></main>
}

function Cart() {
  const [cart,setCart]=useState(null)
  const load=()=>apiFetch('/api/cart/').then(r=>r.ok&&setCart(r.data))
  useEffect(load,[])
  const update=async(row,quantity)=>{await apiFetch(`/api/cart/items/${row.id}/`,{method:'PATCH',body:JSON.stringify({quantity})});load()}
  const remove=async row=>{await apiFetch(`/api/cart/items/${row.id}/`,{method:'DELETE'});load()}
  if(!cart)return <main className="page">Loading…</main>
  return <main className="page cart-page"><div><small>YOUR RENTAL</small><h1>Shopping cart</h1>{cart.items.map(row=><article className="cart-row" key={row.id}><div><h3>{row.gadget_title}</h3><p>₹{Number(row.gadget_price).toLocaleString('en-IN')} / day · Deposit ₹{Number(row.gadget_deposit).toLocaleString('en-IN')}</p></div><div className="quantity"><button onClick={()=>update(row,Math.max(1,row.quantity-1))}>−</button><span>{row.quantity}</span><button onClick={()=>update(row,row.quantity+1)}>+</button></div><strong>₹{(Number(row.gadget_price)*row.quantity).toLocaleString('en-IN')}</strong><button className="icon-button" onClick={()=>remove(row)}><FiTrash2/></button></article>)}{!cart.items.length&&<div className="empty-state">Your cart is empty.</div>}</div><aside className="summary"><h2>Summary</h2><p>Items <strong>{cart.total_items}</strong></p><p>Rental total <strong>₹{Number(cart.total_price).toLocaleString('en-IN')}</strong></p><Link className="primary" to="/checkout">CHECKOUT</Link></aside></main>
}

function Checkout() {
  const navigate=useNavigate()
  const [cart,setCart]=useState(null),[form,setForm]=useState({full_name:'',phone:'',address:'',city:'',state:'',pincode:''}),[payment,setPayment]=useState('COD'),[proof,setProof]=useState('AADHAAR'),[error,setError]=useState('')
  useEffect(()=>{apiFetch('/api/cart/').then(r=>r.ok&&setCart(r.data))},[])
  const place=async e=>{e.preventDefault(); const r=await apiFetch('/api/orders/checkout/',{method:'POST',body:JSON.stringify({payment_method:payment,id_proof:proof,address:form})}); if(r.ok)navigate(`/orders/${r.data.id}`);else setError(r.data.detail||'Could not place order')}
  return <main className="page checkout-page"><form onSubmit={place}><small>SECURE CHECKOUT</small><h1>Delivery details</h1>{error&&<p className="error">{error}</p>}<div className="form-grid">{Object.entries({full_name:'Full name',phone:'Phone',address:'Address',city:'City',state:'State',pincode:'Pincode'}).map(([k,v])=><label key={k}>{v}<input required value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/></label>)}</div><label>Payment method<select value={payment} onChange={e=>setPayment(e.target.value)}><option value="COD">Cash on delivery</option><option value="CARD">Card</option></select></label><label>ID proof<select value={proof} onChange={e=>setProof(e.target.value)}><option value="AADHAAR">Aadhaar</option><option value="PASSPORT">Passport</option><option value="DRIVING LICENCE">Driving Licence</option></select></label><button className="primary">PLACE ORDER</button></form><aside className="summary"><h2>Order summary</h2><p>Cart total <strong>₹{cart?Number(cart.total_price).toLocaleString('en-IN'):'0'}</strong></p><p>Refundable deposit <strong>Excluded</strong></p></aside></main>
}

function Orders() {
  const [orders,setOrders]=useState([])
  useEffect(()=>{apiFetch('/api/orders/').then(r=>r.ok&&setOrders(r.data))},[])
  return <main className="page"><small>MY RENTALS</small><h1>My Orders</h1><div className="order-list">{orders.map(o=><Link className="order-card" key={o.id} to={`/orders/${o.id}`}><div><b>Order #{o.id}</b><small>{new Date(o.created_at).toLocaleDateString()}</small></div><span>{o.rows.every(r=>r.status==='delivered')?'delivered':o.rows.some(r=>r.status==='cancelled')?'cancelled':o.rows.some(r=>r.status==='shipped')?'shipped':'placed'}</span><strong>₹{Number(o.total).toLocaleString('en-IN')}</strong><span>{o.rows.length} items</span></Link>)}</div></main>
}

function OrderDetail() {
  const {id}=useParams(),[order,setOrder]=useState(null)
  const load=()=>apiFetch(`/api/orders/${id}/`).then(r=>r.ok&&setOrder(r.data))
  useEffect(load,[id])
  const cancel=async()=>{await apiFetch(`/api/orders/${id}/`,{method:'POST'});load()}
  if(!order)return <main className="page">Loading…</main>
  return <main className="page order-detail"><div><small>ORDER #{order.id}</small><h1>Order details</h1>{order.rows.map(r=><article className="order-row" key={r.id}><div><h3>{r.gadget_title}</h3><p>{r.quantity} days · ₹{Number(r.gadget_price).toLocaleString('en-IN')} / day</p></div><span className={`status ${r.status}`}>{r.status}</span></article>)}{order.can_cancel&&<button className="danger" onClick={cancel}>CANCEL ORDER</button>}</div><aside className="summary"><h2>Delivery</h2><p>{order.full_name}<br/>{order.address}<br/>{order.city}, {order.state} {order.pincode}</p><p>Phone: {order.phone}</p><p>ID: {order.id_proof}</p><p>Payment: {order.payment_method}</p><p>Total <strong>₹{Number(order.total).toLocaleString('en-IN')}</strong></p></aside></main>
}

function LenderGadgets() {
  const [data,setData]=useState({results:[]}),[search,setSearch]=useState('')
  const load=()=>apiFetch(`/api/lender/gadgets/?search=${encodeURIComponent(search)}`).then(r=>r.ok&&setData(r.data))
  useEffect(() => {
    apiFetch('/api/lender/gadgets/').then(r=>r.ok&&setData(r.data))
  }, [])
  const remove=async g=>{if(!window.confirm(`Delete ${g.title}?`))return; const r=await apiFetch(`/api/gadgets/${g.id}/`,{method:'DELETE'}); if(r.ok)load()}
  return <main className="page"><div className="title-row"><div><small>CATALOG</small><h1>My Gadgets</h1></div><Link className="primary" to="/lender/gadgets/new">ADD GADGET</Link></div><form className="search-row" onSubmit={e=>{e.preventDefault();load()}}><FiSearch/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search gadgets"/><button>Search</button></form><div className="lender-table">{data.results.map(g=><article key={g.id}><div><h3>{g.title}</h3><small>{g.category} · ₹{Number(g.price).toLocaleString('en-IN')} / day</small></div><div><Link to={`/lender/gadgets/${g.id}/edit`}>Edit</Link> <button onClick={()=>remove(g)}>Delete</button></div></article>)}</div></main>
}

function GadgetForm({edit=false}) {
  const {id}=useParams(),navigate=useNavigate()
  const [form,setForm]=useState({title:'',brand:'',deposit:'',in_the_box:'',category:'Cameras',price:'',imageUrl:'',availability:'Available',description:'',is_premium:false})
  useEffect(()=>{if(edit)apiFetch(`/api/gadgets/${id}/`).then(r=>r.ok&&setForm(r.data))},[edit,id])
  const submit=async e=>{e.preventDefault(); const r=await apiFetch(edit?`/api/gadgets/${id}/`:'/api/gadgets/',{method:edit?'PATCH':'POST',body:JSON.stringify(form)}); if(r.ok)navigate('/lender/gadgets')}
  return <main className="page"><form className="auth-card wide" onSubmit={submit}><small>{edit?'EDIT GADGET':'ADD GADGET'}</small><h1>{edit?'Edit Gadget':'Add Gadget'}</h1>{['title','brand','deposit','in_the_box','price','imageUrl','availability','description'].map(k=><label key={k}>{k.replaceAll('_',' ')}<input value={form[k]||''} onChange={e=>setForm({...form,[k]:e.target.value})}/></label>)}<label>Category<select value={form.category} onChange={e=>setForm({...form,category:e.target.value})}><option>Cameras</option><option>Consoles</option><option>Laptops</option><option>Drones</option><option>Projectors</option></select></label><label className="check"><input type="checkbox" checked={form.is_premium} onChange={e=>setForm({...form,is_premium:e.target.checked})}/> Premium gadget</label><button className="primary">SAVE</button></form></main>
}

function LenderOrders() {
  const [rows,setRows]=useState([])
  const load=()=>apiFetch('/api/lender/orders/').then(r=>r.ok&&setRows(r.data))
  useEffect(load,[])
  const advance=async row=>{await apiFetch(`/api/lender/orders/${row.id}/advance/`,{method:'PATCH'});load()}
  return <main className="page"><small>SALES</small><h1>Lender Orders</h1><div className="lender-table">{rows.map(r=><article key={r.id}><div><h3>{r.gadget}</h3><small>Order #{r.order} · {r.quantity} days · ₹{r.amount}</small></div><span className={`status ${r.status}`}>{r.status}</span>{r.status!=='delivered'&&r.status!=='cancelled'&&<button onClick={()=>advance(r)}>Move forward</button>}</article>)}</div></main>
}

function Dashboard() {
  const [d,setD]=useState(null)
  useEffect(()=>{apiFetch('/api/lender/dashboard/').then(r=>r.ok&&setD(r.data))},[])
  if(!d)return <main className="page">Loading…</main>
  const max=Math.max(...d.chart.map(v=>v.sales),1)
  return <main className="page"><small>OVERVIEW</small><h1>Dashboard</h1><div className="stat-grid"><article><small>Total sales</small><strong>₹{Number(d.total_sales).toLocaleString('en-IN')}</strong></article><article><small>Orders</small><strong>{d.total_orders}</strong></article><article><small>Gadgets</small><strong>{d.gadgets}</strong></article><article><small>Still to send</small><strong>{d.still_to_send}</strong></article></div><section className="dashboard-grid"><div className="chart-panel"><h2>Last seven days</h2><div className="chart">{d.chart.map(v=><div key={v.date}><span style={{height:`${Math.max(8,(v.sales/max)*180)}px`}}></span><small>{v.date.slice(5)}</small></div>)}</div></div><div className="summary"><h2>Top gadgets</h2>{d.top_gadgets.map(g=><p key={g.gadget_title}>{g.gadget_title}<strong>{g.sold}</strong></p>)}</div></section></main>
}

function Protected({user,children}){return user?children:<Navigate to="/login"/>}

function App() {
  const [user,setUser]=useState(null)
  useEffect(()=>{apiFetch('/api/users/profile/').then(r=>r.ok&&setUser(r.data))},[])
  const logout=async()=>{const refresh=getRefreshToken(); if(refresh)await apiFetch('/api/users/logout/',{method:'POST',body:JSON.stringify({refresh})}); clearTokens();setUser(null)}
  return <BrowserRouter><Header user={user} logout={logout}/><Routes><Route path="/" element={<Navigate to="/gadgets"/>}/><Route path="/gadgets" element={<Gadgets/>}/><Route path="/gadgets/:id" element={<Detail user={user}/>}/><Route path="/login" element={<Login onLogin={()=>apiFetch('/api/users/profile/').then(r=>r.ok&&setUser(r.data))}/>}/><Route path="/register" element={<Register/>}/><Route path="/cart" element={<Protected user={user}><Cart/></Protected>}/><Route path="/checkout" element={<Protected user={user}><Checkout/></Protected>}/><Route path="/orders" element={<Protected user={user}><Orders/></Protected>}/><Route path="/orders/:id" element={<Protected user={user}><OrderDetail/></Protected>}/><Route path="/lender/gadgets" element={<Protected user={user}><LenderGadgets/></Protected>}/><Route path="/lender/gadgets/new" element={<Protected user={user}><GadgetForm/></Protected>}/><Route path="/lender/gadgets/:id/edit" element={<Protected user={user}><GadgetForm edit/></Protected>}/><Route path="/lender/orders" element={<Protected user={user}><LenderOrders/></Protected>}/><Route path="/lender/dashboard" element={<Protected user={user}><Dashboard/></Protected>}/><Route path="*" element={<main className="page empty-state"><h1>Not Found</h1></main>}/></Routes></BrowserRouter>
}

export default App
