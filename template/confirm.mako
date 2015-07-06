<%inherit file="layout.mako"/>
<%block name="body">
    <div class="content-right">
        <ul>
            <li>
                <label>Registered Email or Wechat</label>
                <input/>
            </li>
             <li>
                <label>New Password</label>
                <input/>
            </li>
            <li>
                <label>Reconfirm New Password</label>
                <input/>
            </li>
            <li>
                <label>Send Verified Code to Email or Wechat</label>
                <button>Yes</button>
            </li>
             <li>
                <label>Verified Code(Send to your email or Wechat)</label>
                <input/>
            </li>
            <li>
                <button>Confirm</button>
            </li>
        </ul>
    </div>
</%block>